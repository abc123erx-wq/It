// ============================================================================
// MODO ONLINE (Firebase Realtime Database) — NÃO faz parte do jogo original.
// Cliente REST do Realtime Database (projeto kaka-ca0ff) via WinHTTP.
// Ver firebase_online.h para a API. Alvo: Windows (o engine é Win32/DirectX).
// ============================================================================

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winhttp.h>

#include <atomic>
#include <cctype>
#include <condition_variable>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <functional>
#include <mutex>
#include <set>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "firebase_online.h"

#pragma comment(lib, "winhttp.lib")

// ---------------------------------------------------------------------------
// Configuração (mesma do hub web online/js/config.js)
// ---------------------------------------------------------------------------
static const wchar_t *kDbHost = L"kaka-ca0ff-default-rtdb.firebaseio.com";
static const char *kDbPrefix = "/bo1z";

// ---------------------------------------------------------------------------
// Mini JSON (parser + escritor) — só o necessário para o formato do RTDB
// ---------------------------------------------------------------------------
struct JsonValue
{
    enum Type { Null, Bool, Num, Str, Arr, Obj };
    Type type = Null;
    bool boolean = false;
    double num = 0.0;
    std::string str;
    std::vector<JsonValue> arr;
    std::vector<std::pair<std::string, JsonValue>> obj;

    const JsonValue *Get(const char *key) const
    {
        if (type != Obj)
            return nullptr;
        for (const auto &kv : obj)
        {
            if (kv.first == key)
                return &kv.second;
        }
        return nullptr;
    }
    std::string GetString(const char *key, const char *def = "") const
    {
        const JsonValue *v = Get(key);
        if (!v || v->type != Str)
            return def;
        return v->str;
    }
    double GetNum(const char *key, double def = 0.0) const
    {
        const JsonValue *v = Get(key);
        if (!v || v->type != Num)
            return def;
        return v->num;
    }
};

static std::string JsonEscape(const std::string &s)
{
    std::string out;
    out.reserve(s.size() + 8);
    for (size_t i = 0; i < s.size(); i++)
    {
        char c = s[i];
        switch (c)
        {
        case '"':  out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\n': out += "\\n";  break;
        case '\r': out += "\\r";  break;
        case '\t': out += "\\t";  break;
        default:
            if ((unsigned char)c < 0x20)
            {
                char buf[8];
                sprintf_s(buf, "\\u%04x", (unsigned char)c);
                out += buf;
            }
            else
            {
                out += c;
            }
        }
    }
    return out;
}

static void JsonSkipWs(const std::string &s, size_t &i)
{
    while (i < s.size() && (s[i] == ' ' || s[i] == '\t' || s[i] == '\n' || s[i] == '\r'))
        i++;
}

static bool JsonParseValue(const std::string &s, size_t &i, JsonValue &out);

static bool JsonParseString(const std::string &s, size_t &i, std::string &out)
{
    if (i >= s.size() || s[i] != '"')
        return false;
    i++;
    out.clear();
    while (i < s.size())
    {
        char c = s[i];
        if (c == '"')
        {
            i++;
            return true;
        }
        if (c == '\\')
        {
            i++;
            if (i >= s.size())
                return false;
            char e = s[i];
            switch (e)
            {
            case '"':  out += '"';  break;
            case '\\': out += '\\'; break;
            case '/':  out += '/';  break;
            case 'n':  out += '\n'; break;
            case 'r':  out += '\r'; break;
            case 't':  out += '\t'; break;
            case 'b':  out += '\b'; break;
            case 'f':  out += '\f'; break;
            case 'u':
                if (i + 4 < s.size())
                {
                    unsigned code = 0;
                    for (int k = 1; k <= 4; k++)
                    {
                        char h = s[i + k];
                        code <<= 4;
                        if (h >= '0' && h <= '9') code |= (unsigned)(h - '0');
                        else if (h >= 'a' && h <= 'f') code |= (unsigned)(h - 'a' + 10);
                        else if (h >= 'A' && h <= 'F') code |= (unsigned)(h - 'A' + 10);
                        else return false;
                    }
                    i += 4;
                    // ASCII / BMP simplificado (suficiente para nomes e textos)
                    if (code < 0x80)
                        out += (char)code;
                    else if (code < 0x800)
                    {
                        out += (char)(0xC0 | (code >> 6));
                        out += (char)(0x80 | (code & 0x3F));
                    }
                    else
                    {
                        out += (char)(0xE0 | (code >> 12));
                        out += (char)(0x80 | ((code >> 6) & 0x3F));
                        out += (char)(0x80 | (code & 0x3F));
                    }
                }
                break;
            default:
                out += e;
            }
            i++;
        }
        else
        {
            out += c;
            i++;
        }
    }
    return false;
}

static bool JsonParseValue(const std::string &s, size_t &i, JsonValue &out)
{
    JsonSkipWs(s, i);
    if (i >= s.size())
        return false;
    char c = s[i];
    if (c == '"')
    {
        out.type = JsonValue::Str;
        return JsonParseString(s, i, out.str);
    }
    if (c == '{')
    {
        out.type = JsonValue::Obj;
        i++;
        JsonSkipWs(s, i);
        if (i < s.size() && s[i] == '}')
        {
            i++;
            return true;
        }
        for (;;)
        {
            JsonSkipWs(s, i);
            std::string key;
            if (!JsonParseString(s, i, key))
                return false;
            JsonSkipWs(s, i);
            if (i >= s.size() || s[i] != ':')
                return false;
            i++;
            JsonValue val;
            if (!JsonParseValue(s, i, val))
                return false;
            out.obj.push_back(std::make_pair(key, std::move(val)));
            JsonSkipWs(s, i);
            if (i < s.size() && s[i] == ',')
            {
                i++;
                continue;
            }
            if (i < s.size() && s[i] == '}')
            {
                i++;
                return true;
            }
            return false;
        }
    }
    if (c == '[')
    {
        out.type = JsonValue::Arr;
        i++;
        JsonSkipWs(s, i);
        if (i < s.size() && s[i] == ']')
        {
            i++;
            return true;
        }
        for (;;)
        {
            JsonValue val;
            if (!JsonParseValue(s, i, val))
                return false;
            out.arr.push_back(std::move(val));
            JsonSkipWs(s, i);
            if (i < s.size() && s[i] == ',')
            {
                i++;
                continue;
            }
            if (i < s.size() && s[i] == ']')
            {
                i++;
                return true;
            }
            return false;
        }
    }
    if (s.compare(i, 4, "true") == 0)
    {
        out.type = JsonValue::Bool;
        out.boolean = true;
        i += 4;
        return true;
    }
    if (s.compare(i, 5, "false") == 0)
    {
        out.type = JsonValue::Bool;
        out.boolean = false;
        i += 5;
        return true;
    }
    if (s.compare(i, 4, "null") == 0)
    {
        out.type = JsonValue::Null;
        i += 4;
        return true;
    }
    // número
    {
        char *end = nullptr;
        double v = strtod(s.c_str() + i, &end);
        if (end == s.c_str() + i)
            return false;
        out.type = JsonValue::Num;
        out.num = v;
        i = (size_t)(end - s.c_str());
        return true;
    }
}

static bool JsonParse(const std::string &s, JsonValue &out)
{
    size_t i = 0;
    if (!JsonParseValue(s, i, out))
        return false;
    JsonSkipWs(s, i);
    return i >= s.size(); // tolera lixo final? exige completo
}

static std::string JsonStr(const std::string &v) { return "\"" + JsonEscape(v) + "\""; }

// ---------------------------------------------------------------------------
// HTTP (WinHTTP, HTTPS)
// ---------------------------------------------------------------------------
struct HttpResponse
{
    bool ok = false;
    long status = 0;
    std::string body;
};

static bool HttpSend(const wchar_t *method, const std::string &pathAndQuery,
                     const std::string &jsonBody, HttpResponse *out)
{
    out->ok = false;
    out->status = 0;
    out->body.clear();

    HINTERNET hSession = WinHttpOpen(L"BO1Zombies-Online/1.0",
                                     WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                     WINHTTP_NO_PROXY_NAME,
                                     WINHTTP_NO_PROXY_BYPASS, 0);
    if (!hSession)
        return false;
    WinHttpSetTimeouts(hSession, 5000, 5000, 8000, 8000);

    HINTERNET hConnect = WinHttpConnect(hSession, kDbHost, INTERNET_DEFAULT_HTTPS_PORT, 0);
    if (!hConnect)
    {
        WinHttpCloseHandle(hSession);
        return false;
    }

    std::wstring wpath(pathAndQuery.begin(), pathAndQuery.end());
    HINTERNET hRequest = WinHttpOpenRequest(hConnect, method, wpath.c_str(), NULL,
                                            WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES,
                                            WINHTTP_FLAG_SECURE);
    if (!hRequest)
    {
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        return false;
    }

    BOOL ok;
    if (jsonBody.empty())
    {
        ok = WinHttpSendRequest(hRequest, L"Accept: application/json\r\n", (DWORD)-1L,
                                WINHTTP_NO_REQUEST_DATA, 0, 0, 0);
    }
    else
    {
        ok = WinHttpSendRequest(hRequest,
                                L"Content-Type: application/json\r\nAccept: application/json\r\n",
                                (DWORD)-1L, (LPVOID)jsonBody.data(),
                                (DWORD)jsonBody.size(), (DWORD)jsonBody.size(), 0);
    }

    if (ok)
        ok = WinHttpReceiveResponse(hRequest, NULL);

    if (ok)
    {
        DWORD status = 0;
        DWORD statusSize = sizeof(status);
        WinHttpQueryHeaders(hRequest,
                            WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                            WINHTTP_HEADER_NAME_BY_INDEX, &status, &statusSize,
                            WINHTTP_NO_HEADER_INDEX);
        out->status = (long)status;

        for (;;)
        {
            DWORD avail = 0;
            if (!WinHttpQueryDataAvailable(hRequest, &avail) || avail == 0)
                break;
            std::vector<char> buf(avail);
            DWORD read = 0;
            if (!WinHttpReadData(hRequest, buf.data(), avail, &read) || read == 0)
                break;
            out->body.append(buf.data(), read);
        }
        out->ok = true;
    }

    WinHttpCloseHandle(hRequest);
    WinHttpCloseHandle(hConnect);
    WinHttpCloseHandle(hSession);
    return out->ok;
}

static std::string MakePath(const char *suffix)
{
    // suffix como "rooms/AB12CD/players.json" → "/bo1z/rooms/AB12CD/players.json"
    std::string p = kDbPrefix;
    p += "/";
    p += suffix;
    return p;
}

// ---------------------------------------------------------------------------
// Estado global do módulo
// ---------------------------------------------------------------------------
struct OnlineEvent
{
    std::string type;
    std::string f1;
    std::string f2;
    std::string f3;
};

struct RosterEntry
{
    std::string name;
    std::string ready;
    std::string points;
    std::string kills;
    std::string downs;
    std::string alive;
};

static std::mutex g_stateMutex;
static std::string g_status = "off";
static std::string g_uid;
static std::string g_name;
static std::string g_roomCode;
static bool g_enabled = false;

static std::vector<OnlineEvent> g_batch;   // lote atual (lido por Online_GetEvent)
static std::deque<OnlineEvent> g_inbox;    // eventos recém-chegados (aguardando poll)
static std::vector<RosterEntry> g_roster;
static std::deque<std::string> g_seenOrder;
static std::set<std::string> g_seenKeys;
static bool g_pollInFlight = false;

// fila de trabalhos (thread de rede)
static std::mutex g_jobMutex;
static std::condition_variable g_jobCv;
static std::deque<std::function<void()>> g_jobs;
static std::atomic<bool> g_running(false);
static std::thread g_worker;

static void QueueJob(std::function<void()> job)
{
    {
        std::lock_guard<std::mutex> lk(g_jobMutex);
        // rede lenta/offline: abandona os jobs mais antigos em vez de acumular
        while (g_jobs.size() >= 64)
            g_jobs.pop_front();
        g_jobs.push_back(std::move(job));
    }
    g_jobCv.notify_one();
}

static void WorkerLoop()
{
    for (;;)
    {
        std::function<void()> job;
        {
            std::unique_lock<std::mutex> lk(g_jobMutex);
            g_jobCv.wait(lk, [] { return !g_jobs.empty() || !g_running; });
            if (!g_running && g_jobs.empty())
                return;
            job = std::move(g_jobs.front());
            g_jobs.pop_front();
        }
        job();
    }
}

static void MarkError(long status)
{
    std::lock_guard<std::mutex> lk(g_stateMutex);
    if (status == 401 || status == 403)
        g_status = "erro: permissao negada (401/403)";
    else if (status > 0)
        g_status = "erro: http " + std::to_string(status);
    else
        g_status = "erro: rede";
}

// ---------------------------------------------------------------------------
// Poll: busca o nó inteiro da sala e calcula o diff de eventos/roster
// ---------------------------------------------------------------------------
static void PollRoomNode()
{
    std::string code;
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        code = g_roomCode;
    }
    if (code.empty())
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        g_pollInFlight = false;
        return;
    }

    HttpResponse resp;
    std::string path = MakePath(("rooms/" + code + ".json").c_str());
    bool ok = HttpSend(L"GET", path, "", &resp);
    if (!ok || resp.status < 200 || resp.status >= 300)
    {
        if (ok)
            MarkError(resp.status);
        std::lock_guard<std::mutex> lk(g_stateMutex);
        g_pollInFlight = false;
        return;
    }

    JsonValue root;
    if (!JsonParse(resp.body, root) || root.type != JsonValue::Obj)
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        g_pollInFlight = false;
        return;
    }

    std::lock_guard<std::mutex> lk(g_stateMutex);
    g_pollInFlight = false;

    if (g_status == "connecting")
        g_status = "online";

    // ---- eventos novos (diff por chave) ----
    const JsonValue *events = root.Get("events");
    if (events && events->type == JsonValue::Obj)
    {
        for (const auto &kv : events->obj)
        {
            if (g_seenKeys.find(kv.first) != g_seenKeys.end())
                continue;
            g_seenKeys.insert(kv.first);
            g_seenOrder.push_back(kv.first);
            while (g_seenOrder.size() > 256)
            {
                g_seenKeys.erase(g_seenOrder.front());
                g_seenOrder.pop_front();
            }

            const JsonValue &e = kv.second;
            OnlineEvent ev;
            ev.type = e.GetString("type", "evento");
            if (ev.type == "kill" || ev.type == "down" || ev.type == "revive")
            {
                ev.f1 = e.GetString("name", "?");
            }
            else if (ev.type == "round_start")
            {
                double r = e.GetNum("round", 0);
                ev.f1 = std::to_string((long long)r);
            }
            else if (ev.type == "chat")
            {
                ev.f1 = e.GetString("name", "?");
                ev.f2 = e.GetString("text", "");
            }
            g_inbox.push_back(ev);
            while (g_inbox.size() > 128)
                g_inbox.pop_front();
        }
    }

    // ---- roster ----
    g_roster.clear();
    const JsonValue *players = root.Get("players");
    if (players && players->type == JsonValue::Obj)
    {
        for (const auto &kv : players->obj)
        {
            const JsonValue &p = kv.second;
            RosterEntry r;
            r.name = p.GetString("name", "?");
            const JsonValue *ready = p.Get("ready");
            r.ready = (ready && ready->type == JsonValue::Bool && ready->boolean) ? "1" : "0";
            const JsonValue *st = p.Get("state");
            if (st && st->type == JsonValue::Obj)
            {
                r.points = std::to_string((long long)st->GetNum("points", 0));
                r.kills = std::to_string((long long)st->GetNum("kills", 0));
                r.downs = std::to_string((long long)st->GetNum("downs", 0));
                const JsonValue *alive = st->Get("alive");
                r.alive = (alive && alive->type == JsonValue::Bool && !alive->boolean) ? "0" : "1";
            }
            else
            {
                r.points = "0";
                r.kills = "0";
                r.downs = "0";
                r.alive = "1";
            }
            g_roster.push_back(r);
        }
    }
}

// ---------------------------------------------------------------------------
// API pública
// ---------------------------------------------------------------------------
void Online_Init()
{
    if (g_running)
        return;
    g_running = true;
    g_worker = std::thread(WorkerLoop);
    std::lock_guard<std::mutex> lk(g_stateMutex);
    if (g_status == "off")
        g_status = "connecting";
    g_enabled = true;
}

void Online_Shutdown()
{
    if (g_running)
    {
        g_running = false;
        g_jobCv.notify_all();
        if (g_worker.joinable())
            g_worker.join();
    }
    std::lock_guard<std::mutex> lk(g_stateMutex);
    g_status = "off";
    g_roomCode.clear();
    g_enabled = false;
}

static std::string MakeUid(const char *name)
{
    // FNV-1a do nome + pid: estável por sessão, sem dependências externas
    unsigned long long h = 1469598103934665603ULL;
    for (const char *p = name; *p; p++)
    {
        h ^= (unsigned char)*p;
        h *= 1099511628211ULL;
    }
    char buf[80];
    sprintf_s(buf, "game-%08lx%08lx-%04x",
              (unsigned long)(h >> 32), (unsigned long)(h & 0xFFFFFFFFu),
              (unsigned)(GetCurrentProcessId() & 0xFFFF));
    return std::string(buf);
}

int Online_Connect(const char *name)
{
    Online_Init();
    std::lock_guard<std::mutex> lk(g_stateMutex);
    if (!name || !name[0])
        name = "Operador";
    g_name = name;
    g_uid = MakeUid(name);
    if (g_status == "off")
        g_status = "connecting";

    // presença básica no hub web
    std::string path = MakePath(("players/" + g_uid + ".json").c_str());
    std::string body = std::string("{") +
        "\"name\":" + JsonStr(g_name) + "," +
        "\"status\":\"online\"," +
        "\"lastSeen\":{\".sv\":\"timestamp\"}" +
        "}";
    QueueJob([path, body]() {
        HttpResponse resp;
        if (HttpSend(L"PATCH", path, body, &resp))
        {
            if (resp.status < 200 || resp.status >= 300)
                MarkError(resp.status);
        }
    });
    return 1;
}

const char *Online_Status()
{
    static std::string buf;
    std::lock_guard<std::mutex> lk(g_stateMutex);
    buf = g_status;
    return buf.c_str();
}

int Online_IsOnline()
{
    std::lock_guard<std::mutex> lk(g_stateMutex);
    return (g_status == "online" || g_status.compare(0, 5, "room:") == 0) ? 1 : 0;
}

static std::string GenCode()
{
    static const char *alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    std::string code;
    for (int i = 0; i < 6; i++)
        code += alphabet[rand() % 32];
    return code;
}

const char *Online_CreateRoom(const char *roomName, const char *mapName, const char *mode, int maxPlayers)
{
    static std::string result;
    result.clear();
    if (!roomName || !roomName[0])
        roomName = "Sala";
    if (!mapName || !mapName[0])
        mapName = "zombie_theater";
    if (!mode || !mode[0])
        mode = "survival";
    if (maxPlayers < 2 || maxPlayers > 8)
        maxPlayers = 4;

    std::string name, uid;
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        name = g_name;
        uid = g_uid;
    }
    if (uid.empty())
        Online_Connect(name.empty() ? "Operador" : name.c_str());
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        name = g_name;
        uid = g_uid;
    }

    for (int attempt = 0; attempt < 5; attempt++)
    {
        std::string code = GenCode();

        // existe?
        HttpResponse resp;
        std::string getPath = MakePath(("rooms/" + code + ".json").c_str());
        if (!HttpSend(L"GET", getPath, "", &resp))
        {
            MarkError(0);
            return "";
        }
        if (resp.status == 200 && resp.body != "null" && !resp.body.empty())
            continue; // código ocupado

        std::string body = std::string("{") +
            "\"code\":" + JsonStr(code) + "," +
            "\"name\":" + JsonStr(roomName) + "," +
            "\"map\":" + JsonStr(mapName) + "," +
            "\"mode\":" + JsonStr(mode) + "," +
            "\"maxPlayers\":" + std::to_string(maxPlayers) + "," +
            "\"hostId\":" + JsonStr(uid) + "," +
            "\"hostName\":" + JsonStr(name) + "," +
            "\"status\":\"waiting\"," +
            "\"createdAt\":{\".sv\":\"timestamp\"}," +
            "\"match\":{\"round\":0,\"kills\":0,\"downs\":0,\"points\":0,\"startedAt\":null}," +
            "\"players\":{" + JsonStr(uid) + ":{\"name\":" + JsonStr(name) +
                ",\"isHost\":true,\"ready\":false,\"joinedAt\":{\".sv\":\"timestamp\"}," +
                "\"state\":{\"alive\":true,\"points\":0,\"kills\":0,\"downs\":0}}}" +
            "}";

        HttpResponse putResp;
        if (!HttpSend(L"PUT", MakePath(("rooms/" + code + ".json").c_str()), body, &putResp))
        {
            MarkError(0);
            return "";
        }
        if (putResp.status < 200 || putResp.status >= 300)
        {
            MarkError(putResp.status);
            return "";
        }

        {
            std::lock_guard<std::mutex> lk(g_stateMutex);
            g_roomCode = code;
            g_status = "room:" + code;
            g_batch.clear();
            g_inbox.clear();
            g_seenKeys.clear();
            g_seenOrder.clear();
            g_roster.clear();
        }
        result = code;
        return result.c_str();
    }
    return "";
}

int Online_JoinRoom(const char *code)
{
    if (!code || !code[0])
        return 0;
    std::string roomCode = code;
    for (size_t i = 0; i < roomCode.size(); i++)
        roomCode[i] = (char)toupper((unsigned char)roomCode[i]);

    std::string name, uid;
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        name = g_name;
        uid = g_uid;
    }
    if (uid.empty())
    {
        Online_Connect(name.empty() ? "Operador" : name.c_str());
        std::lock_guard<std::mutex> lk(g_stateMutex);
        name = g_name;
        uid = g_uid;
    }

    // a sala existe?
    HttpResponse resp;
    if (!HttpSend(L"GET", MakePath(("rooms/" + roomCode + ".json").c_str()), "", &resp))
    {
        MarkError(0);
        return 0;
    }
    if (resp.status != 200 || resp.body == "null" || resp.body.empty())
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        g_status = "erro: sala nao encontrada";
        return 0;
    }

    std::string body = std::string("{") +
        "\"name\":" + JsonStr(name) + "," +
        "\"isHost\":false,\"ready\":false," +
        "\"joinedAt\":{\".sv\":\"timestamp\"}," +
        "\"state\":{\"alive\":true,\"points\":0,\"kills\":0,\"downs\":0}" +
        "}";
    HttpResponse putResp;
    if (!HttpSend(L"PUT", MakePath(("rooms/" + roomCode + "/players/" + uid + ".json").c_str()),
                  body, &putResp))
    {
        MarkError(0);
        return 0;
    }
    if (putResp.status < 200 || putResp.status >= 300)
    {
        MarkError(putResp.status);
        return 0;
    }

    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        g_roomCode = roomCode;
        g_status = "room:" + roomCode;
        g_batch.clear();
        g_inbox.clear();
        g_seenKeys.clear();
        g_seenOrder.clear();
        g_roster.clear();
        g_pollInFlight = false;
    }
    return 1;
}

void Online_LeaveRoom()
{
    std::string code, uid;
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        code = g_roomCode;
        uid = g_uid;
        g_roomCode.clear();
        g_status = uid.empty() ? "off" : "online";
    }
    if (!code.empty() && !uid.empty())
    {
        std::string path = MakePath(("rooms/" + code + "/players/" + uid + ".json").c_str());
        QueueJob([path]() {
            HttpResponse resp;
            HttpSend(L"DELETE", path, "", &resp);
        });
    }
}

const char *Online_GetRoomCode()
{
    static std::string buf;
    std::lock_guard<std::mutex> lk(g_stateMutex);
    buf = g_roomCode;
    return buf.c_str();
}

void Online_Say(const char *text)
{
    if (!text || !text[0])
        return;
    std::string code, uid, name;
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        code = g_roomCode;
        uid = g_uid;
        name = g_name;
    }
    if (code.empty())
        return;
    std::string body = std::string("{") +
        "\"uid\":" + JsonStr(uid) + "," +
        "\"name\":" + JsonStr(name) + "," +
        "\"text\":" + JsonStr(text) + "," +
        "\"ts\":{\".sv\":\"timestamp\"}" +
        "}";
    std::string path = MakePath(("rooms/" + code + "/chat.json").c_str());
    QueueJob([path, body]() {
        HttpResponse resp;
        HttpSend(L"POST", path, body, &resp);
    });
}

void Online_PushState(int round, int alive, int kills, int downs, int points)
{
    std::string code, uid;
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        code = g_roomCode;
        uid = g_uid;
    }
    if (code.empty() || uid.empty())
        return;

    std::string body = std::string("{") +
        "\"state\":{\"alive\": " + (alive ? "true" : "false") + "," +
        "\"points\":" + std::to_string(points) + "," +
        "\"kills\":" + std::to_string(kills) + "," +
        "\"downs\":" + std::to_string(downs) + "}," +
        "\"lastSeen\":{\".sv\":\"timestamp\"}" +
        "}";
    std::string path = MakePath(("rooms/" + code + "/players/" + uid + ".json").c_str());
    QueueJob([path, body]() {
        HttpResponse resp;
        HttpSend(L"PATCH", path, body, &resp);
    });

    if (round > 0)
    {
        std::string matchBody = "{\"round\":" + std::to_string(round) + "}";
        std::string matchPath = MakePath(("rooms/" + code + "/match.json").c_str());
        QueueJob([matchPath, matchBody]() {
            HttpResponse resp;
            HttpSend(L"PATCH", matchPath, matchBody, &resp);
        });
    }
}

void Online_PushEvent(const char *type, const char *dataJson)
{
    if (!type || !type[0])
        return;
    std::string code;
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        code = g_roomCode;
    }
    if (code.empty())
        return;

    std::string payload = dataJson ? dataJson : "{}";
    if (payload.empty() || payload[0] != '{')
        payload = "{}";
    // injeta type + timestamp dentro do objeto
    std::string body = payload;
    if (body.size() <= 2)
        body = "{\"type\":" + JsonStr(type) + ",\"ts\":{\".sv\":\"timestamp\"}}";
    else
        body = "{\"type\":" + JsonStr(type) + "," + body.substr(1);

    std::string path = MakePath(("rooms/" + code + "/events.json").c_str());
    QueueJob([path, body]() {
        HttpResponse resp;
        HttpSend(L"POST", path, body, &resp);
    });
}

int Online_Poll()
{
    // coleta o lote atual para leitura via Online_GetEvent
    {
        std::lock_guard<std::mutex> lk(g_stateMutex);
        g_batch.assign(g_inbox.begin(), g_inbox.end());
        g_inbox.clear();

        std::string code = g_roomCode;
        if (code.empty())
            return (int)g_batch.size();
        if (g_pollInFlight)
            return (int)g_batch.size();
        g_pollInFlight = true;
    }

    QueueJob([]() { PollRoomNode(); });
    std::lock_guard<std::mutex> lk(g_stateMutex);
    return (int)g_batch.size();
}

const char *Online_GetEvent(int i, int field)
{
    static std::string buf;
    std::lock_guard<std::mutex> lk(g_stateMutex);
    buf.clear();
    if (i < 0 || i >= (int)g_batch.size())
        return buf.c_str();
    const OnlineEvent &e = g_batch[i];
    switch (field)
    {
    case 0: buf = e.type; break;
    case 1: buf = e.f1; break;
    case 2: buf = e.f2; break;
    case 3: buf = e.f3; break;
    default: break;
    }
    return buf.c_str();
}

int Online_RosterCount()
{
    std::lock_guard<std::mutex> lk(g_stateMutex);
    return (int)g_roster.size();
}

const char *Online_GetRoster(int i, int field)
{
    static std::string buf;
    std::lock_guard<std::mutex> lk(g_stateMutex);
    buf.clear();
    if (i < 0 || i >= (int)g_roster.size())
        return buf.c_str();
    const RosterEntry &r = g_roster[i];
    switch (field)
    {
    case 0: buf = r.name; break;
    case 1: buf = r.ready; break;
    case 2: buf = r.points; break;
    case 3: buf = r.kills; break;
    case 4: buf = r.downs; break;
    case 5: buf = r.alive; break;
    default: break;
    }
    return buf.c_str();
}
