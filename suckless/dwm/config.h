/* See LICENSE file for copyright and license details. */

#include <X11/XF86keysym.h>

/* appearance */
static const unsigned int borderpx = 2; /* border pixel of windows */
static const unsigned int gappx     = 12;        /* gaps between windows */
static const unsigned int snap = 32;    /* snap pixel */
static const int showbar = 0;           /* 0 means no bar */
static const int topbar = 1;            /* 0 means bottom bar */
static const char *fonts[] = {"monospace:size=10"};
static const char dmenufont[] = "monospace:size=10";
static char normbgcolor[] = "#222222";
static char normbordercolor[] = "#444444";
static char normfgcolor[] = "#bbbbbb";
static char selfgcolor[] = "#eeeeee";
static char selbordercolor[] = "#005577";
static char selbgcolor[] = "#005577";
static char *colors[][3] = {
    /*               fg           bg           border   */
    [SchemeNorm] = {normfgcolor, normbgcolor, normbordercolor},
    [SchemeSel] = {selfgcolor, selbgcolor, selbordercolor},
};

/* tagging */
static const char *tags[] = {"1", "2", "3", "4", "5", "6", "7", "8", "9"};

static const Rule rules[] = {
    /* xprop(1):
     *	WM_CLASS(STRING) = instance, class
     *	WM_NAME(STRING) = title
     */
    /* class      instance    title       tags mask     isfloating   monitor */
    {"Gimp", NULL, NULL, 0, 0, -1},
    /*{"Firefox", NULL, NULL, 1 << 8, 0, -1},*/
};

/* layout(s) */
static const float mfact = 0.65; /* factor of master area size [0.05..0.95] */
static const int nmaster = 1;    /* number of clients in master area */
static const int resizehints =
    0; /* 1 means respect size hints in tiled resizals */
static const int lockfullscreen =
    1; /* 1 will force focus on the fullscreen window */

static const Layout layouts[] = {
    /* symbol     arrange function */
    {"[\\]", dwindle}, /* first entry is default */
    {"[]=", tile},
    {"><>", NULL}, /* no layout function means floating behavior */
    {"[M]", monocle},
};

/* key definitions */
#define MODKEY Mod4Mask
#define TAGKEYS(KEY, TAG)                                                      \
  {MODKEY, KEY, view, {.ui = 1 << TAG}},                                       \
      {MODKEY | ControlMask, KEY, toggleview, {.ui = 1 << TAG}},               \
      {MODKEY | ShiftMask, KEY, tag, {.ui = 1 << TAG}}, {                      \
    MODKEY | ControlMask | ShiftMask, KEY, toggletag, { .ui = 1 << TAG }       \
  }
#define SPAWN(KEY, CMD)                                                        \
  {                                                                            \
    MODKEY, KEY, spawn, { .v = CMD }                                           \
  }
#define WIN_KEY(KEY) MODKEY | ShiftMask, KEY

/* helper for spawning shell commands in the pre dwm-5.0 fashion */
#define SHCMD(cmd)                                                             \
  {                                                                            \
    .v = (const char *[]) { "/bin/sh", "-c", cmd, NULL }                       \
  }

/* commands */
static char dmenumon[2] =
    "0"; /* component of dmenucmd, manipulated in spawn() */
static const char *dmenucmd[] = {"dmenu_run",    "-fn", dmenufont,   "-nb",
                                 normbgcolor,    "-nf", normfgcolor, "-sb",
                                 selbordercolor, "-sf", selfgcolor,  NULL};
static const char *termcmd[] = {"st", NULL};
static const char *browsercmd[] = {"zen-browser", NULL};
static const char *discordcmd[] = {"vesktop", NULL};
static const char *pavucmd[] = {"pavucontrol", NULL};
static const char *gimpcmd[] = {"gimp", NULL};
static const char *lockcmd[] = {"slock", NULL};
static const char *freetube[] = {"freetube", NULL};
static const char *light_up[] = {"light", "0", NULL};
static const char *light_down[] = {"light", "1", NULL};
static const char scratchpadname[] = "scratchpad";
static const char *scratchpadcmd[] = {"st", "-t",     scratchpadname,
                                      "-g", "120x34", NULL};

static const Key keys[] = {
    /* modifier                     key        function        argument */
    SPAWN(XK_space, dmenucmd),
    SPAWN(XK_t, termcmd),
    SPAWN(XK_Return, termcmd),
    SPAWN(XK_b, browsercmd),
    SPAWN(XK_d, discordcmd),
    SPAWN(XK_p, pavucmd),
    SPAWN(XK_g, gimpcmd),
    SPAWN(XK_l, lockcmd),
    SPAWN(XK_f, freetube),
    SPAWN(XF86XK_MonBrightnessDown, light_down),
    SPAWN(XF86XK_MonBrightnessUp, light_up),
	  { MODKEY,                       XK_grave,  togglescratch,  {.v = scratchpadcmd } },
    { MODKEY,                       XK_r,      setlayout,      {.v = &layouts[0]} },
    { MODKEY|ShiftMask,             XK_r,      setlayout,      {.v = &layouts[1]} },
    {WIN_KEY(XK_0), tag, {.ui = ~0}},
    {MODKEY, XK_0, view, {.ui = ~0}},
    TAGKEYS(XK_1, 0),
    TAGKEYS(XK_2, 1),
    TAGKEYS(XK_3, 2),
    TAGKEYS(XK_4, 3),
    TAGKEYS(XK_5, 4),
    TAGKEYS(XK_6, 5),
    TAGKEYS(XK_7, 6),
    TAGKEYS(XK_8, 7),
    TAGKEYS(XK_9, 8),
    {WIN_KEY(XK_space), zoom, {0}},
    {WIN_KEY(XK_r), xrdb, {.v = NULL}},
    {WIN_KEY(XK_q), quit, {0}},
    {WIN_KEY(XK_j), focusstack, {.i = +1}},
    {WIN_KEY(XK_k), focusstack, {.i = -1}},
    {WIN_KEY(XK_i), incnmaster, {.i = +1}},
    {WIN_KEY(XK_d), incnmaster, {.i = -1}},
    {WIN_KEY(XK_h), setmfact, {.f = -0.05}},
    {WIN_KEY(XK_l), setmfact, {.f = +0.05}},
    {WIN_KEY(XK_b), togglebar, {0}},
    {MODKEY, XK_comma, focusmon, {.i = -1}},
    {MODKEY, XK_period, focusmon, {.i = +1}},
    {MODKEY | ShiftMask, XK_comma, tagmon, {.i = -1}},
    {MODKEY | ShiftMask, XK_period, tagmon, {.i = +1}},
    {WIN_KEY(XK_c), killclient, {0}},
};

/* button definitions */
/* click can be ClkTagBar, ClkLtSymbol, ClkStatusText, ClkWinTitle,
 * ClkClientWin, or ClkRootWin */
static const Button buttons[] = {
    /* click                event mask      button          function argument */
    {ClkLtSymbol, 0, Button1, setlayout, {0}},
    {ClkLtSymbol, 0, Button3, setlayout, {.v = &layouts[2]}},
    {ClkWinTitle, 0, Button2, zoom, {0}},
    {ClkStatusText, 0, Button2, spawn, {.v = termcmd}},
    {ClkClientWin, MODKEY, Button1, movemouse, {0}},
    {ClkClientWin, MODKEY, Button2, togglefloating, {0}},
    {ClkClientWin, MODKEY, Button3, resizemouse, {0}},
    {ClkTagBar, 0, Button1, view, {0}},
    {ClkTagBar, 0, Button3, toggleview, {0}},
    {ClkTagBar, MODKEY, Button1, tag, {0}},
    {ClkTagBar, MODKEY, Button3, toggletag, {0}},
};
