// ONLINE MOD - registro nos hooks do mod stack (mods/_stack/maps/_modstack.gsc).
// Carregamento: +set fs_mods "online" (sozinho ou em pilha: "online zinfo", "horde online zinfo", ...)

register()
{
	// main_end do shared hook de todo mapa e o hook próprio do Five
	maps\_modstack::add( "_zombiemode_ffotd::main_end", maps\online\_online::main_end_any_map );
	maps\_modstack::add( "zombie_pentagon_ffotd::main_end", maps\online\_online::main_end_any_map );
}
