import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from datetime import datetime

# ─────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────

USER_DATA_FILE = "user_data.json"
MIN_BET = 10

SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "⭐", "🔔", "💎"]

CARD_VALUES = {
    "A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10
}
CARD_SUITS   = ["♠", "♥", "♦", "♣"]
CARD_NUMBERS = list(CARD_VALUES.keys())

ROULETTE_RED = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
ROULETTE_BLACK = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

WHEEL_SEGMENTS = [
    {"label": "💥 x0",   "multiplier": 0,    "weight": 20},
    {"label": "😢 x0",   "multiplier": 0,    "weight": 15},
    {"label": "🔄 x1",   "multiplier": 1,    "weight": 15},
    {"label": "🎯 x1.5", "multiplier": 1.5,  "weight": 20},
    {"label": "🎊 x2",   "multiplier": 2,    "weight": 15},
    {"label": "⭐ x3",   "multiplier": 3,    "weight": 8},
    {"label": "💎 x5",   "multiplier": 5,    "weight": 5},
    {"label": "👑 x10",  "multiplier": 10,   "weight": 1.5},
    {"label": "🔥 x25",  "multiplier": 25,   "weight": 0.5},
]


# ─────────────────────────────────────────────
#  Helpers données
# ─────────────────────────────────────────────

def load_data() -> dict:
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def save_data(data: dict) -> None:
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_points(user_id: int) -> float:
    return load_data().get(str(user_id), {}).get("points", 0.0)

def set_points(user_id: int, amount: float) -> None:
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {}
    data[uid]["points"] = round(amount, 2)
    save_data(data)

def add_points(user_id: int, delta: float) -> float:
    """Ajoute (ou retire si négatif) des points. Retourne le nouveau solde."""
    new = round(get_points(user_id) + delta, 2)
    set_points(user_id, new)
    return new

def fmt(n: float) -> str:
    """Formate un nombre avec séparateur de milliers."""
    return f"{n:,.2f}".rstrip("0").rstrip(".")


# ─────────────────────────────────────────────
#  Helpers Discord
# ─────────────────────────────────────────────

def result_embed(title: str, won: bool, bet: float, profit: float, new_bal: float,
                 description: str = "") -> discord.Embed:
    """Embed de résultat standardisé."""
    color = 0x2ecc71 if won else 0xe74c3c
    embed = discord.Embed(title=title, description=description, color=color)
    sign  = "+" if profit >= 0 else ""
    embed.add_field(name="💰 Mise",    value=f"{fmt(bet)} pts",            inline=True)
    embed.add_field(name="📊 Résultat", value=f"{sign}{fmt(profit)} pts",  inline=True)
    embed.add_field(name="💳 Solde",   value=f"{fmt(new_bal)} pts",        inline=True)
    return embed

async def check_bet(ctx, bet: int | None) -> bool:
    """Vérifie la mise et les fonds. Envoie un message d'erreur si invalide."""
    if bet is None:
        await ctx.send(f"❌ Usage : `j!{ctx.invoked_with} <mise>`", delete_after=8)
        return False
    if bet < MIN_BET:
        await ctx.send(f"❌ Mise minimum : **{MIN_BET}** points.", delete_after=8)
        return False
    if bet > get_points(ctx.author.id):
        await ctx.send("❌ Solde insuffisant.", delete_after=8)
        return False
    return True


# ─────────────────────────────────────────────
#  Cog Casino
# ─────────────────────────────────────────────

class Casino(commands.Cog, name="Casino"):
    """Jeux de casino utilisant le système de points."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._active: set[int] = set()   # anti-spam : IDs des joueurs actifs

    # ── garde : empêche de lancer deux jeux en même temps ──────────────────
    def _lock(self, user_id: int) -> bool:
        if user_id in self._active:
            return False
        self._active.add(user_id)
        return True

    def _unlock(self, user_id: int) -> None:
        self._active.discard(user_id)

    # ═══════════════════════════════════════════════════════════════════════
    #  COINFLIP
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="coinflip", aliases=["cf", "pile", "face"])
    async def coinflip(self, ctx, bet: int = None, choice: str = None):
        """Pile ou face. Usage : `j!coinflip <mise> <pile|face>`"""
        if not await check_bet(ctx, bet):
            return

        if choice is None or choice.lower() not in ("pile", "face", "p", "f"):
            await ctx.send("❌ Choisis `pile` ou `face`.", delete_after=8)
            return

        player_choice = "pile" if choice.lower() in ("pile", "p") else "face"

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return

        try:
            msg = await ctx.send(embed=discord.Embed(
                title="🪙 Pile ou Face",
                description="La pièce tourne…",
                color=0xf39c12
            ))

            await asyncio.sleep(1.5)

            result = random.choice(("pile", "face"))
            won    = result == player_choice
            profit = bet if won else -bet
            new_bal = add_points(ctx.author.id, profit)

            coin_emoji = "🟡 PILE" if result == "pile" else "⚪ FACE"
            desc = f"La pièce tombe sur **{coin_emoji}** !\nTu avais misé sur **{player_choice}**."

            embed = result_embed(
                title="🪙 Pile ou Face — " + ("Victoire !" if won else "Défaite"),
                won=won, bet=bet, profit=profit, new_bal=new_bal,
                description=desc
            )
            await msg.edit(embed=embed)

        finally:
            self._unlock(ctx.author.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  MACHINE À SOUS
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="slot", aliases=["slots", "machine"])
    async def slot(self, ctx, bet: int = None):
        """Machine à sous. Usage : `j!slot <mise>`"""
        if not await check_bet(ctx, bet):
            return

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return

        try:
            msg = await ctx.send(embed=discord.Embed(
                title="🎰 Machine à Sous",
                description="❓ ❓ ❓\nLes rouleaux tournent…",
                color=0xe91e63
            ))

            # animation
            for _ in range(6):
                s = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
                await msg.edit(embed=discord.Embed(
                    title="🎰 Machine à Sous — Spinning…",
                    description=" | ".join(s),
                    color=0xe91e63
                ))
                await asyncio.sleep(0.4)

            # résultat final
            reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]

            if reels[0] == reels[1] == reels[2]:
                sym = reels[0]
                multiplier = {
                    "💎": 50, "⭐": 25, "🔔": 15,
                    "🍒": 8,  "🍋": 8,  "🍊": 8, "🍇": 8
                }.get(sym, 8)
                outcome = f"**TRIPLE {sym}** — x{multiplier}"
            elif len(set(reels)) == 2:   # une paire
                multiplier = 2
                outcome = "**Paire !** — x2"
            elif "💎" in reels:
                multiplier = 3
                outcome = "**Bonus Diamant** — x3"
            else:
                multiplier = 0
                outcome = "Aucune combinaison"

            gross   = bet * multiplier
            profit  = gross - bet
            new_bal = add_points(ctx.author.id, profit)
            won     = profit >= 0

            embed = result_embed(
                title="🎰 Machine à Sous — " + ("Victoire !" if won else "Défaite"),
                won=won, bet=bet, profit=profit, new_bal=new_bal,
                description=" | ".join(reels) + f"\n{outcome}"
            )
            await msg.edit(embed=embed)

        finally:
            self._unlock(ctx.author.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  BLACKJACK
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="blackjack", aliases=["bj", "21"])
    async def blackjack(self, ctx, bet: int = None):
        """Blackjack interactif. Usage : `j!blackjack <mise>`"""
        if not await check_bet(ctx, bet):
            return

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return

        def build_deck():
            deck = [f"{n}{s}" for s in CARD_SUITS for n in CARD_NUMBERS]
            random.shuffle(deck)
            return deck

        def hand_total(hand: list[str]) -> int:
            total, aces = 0, 0
            for card in hand:
                num = card[:-1]          # retire le signe de couleur (1 char)
                total += CARD_VALUES[num]
                if num == "A":
                    aces += 1
            while total > 21 and aces:
                total -= 10
                aces -= 1
            return total

        def hand_str(hand: list[str]) -> str:
            return "  ".join(hand)

        def make_embed(player: list, dealer: list, reveal: bool = False, title: str = "🃏 Blackjack") -> discord.Embed:
            pt = hand_total(player)
            dt = hand_total(dealer)
            embed = discord.Embed(title=title, color=0x2e8b57)
            embed.add_field(
                name=f"🎴 Votre main ({pt})",
                value=hand_str(player),
                inline=False
            )
            if reveal:
                embed.add_field(
                    name=f"🎭 Croupier ({dt})",
                    value=hand_str(dealer),
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎭 Croupier (?)",
                    value=f"{dealer[0]}  🂠",
                    inline=False
                )
            embed.add_field(name="💰 Mise", value=f"{fmt(bet)} pts", inline=True)
            embed.set_footer(text="🇭 Tirer  •  🇸 Rester  •  🇩 Doubler (si 2 cartes)")
            return embed

        try:
            deck   = build_deck()
            player = [deck.pop(), deck.pop()]
            dealer = [deck.pop(), deck.pop()]

            msg = await ctx.send(embed=make_embed(player, dealer))
            await msg.add_reaction("🇭")
            await msg.add_reaction("🇸")
            if hand_total(player) in (9, 10, 11):
                await msg.add_reaction("🇩")

            # ── bj naturel ──────────────────────────────────────────────
            if hand_total(player) == 21:
                profit  = int(bet * 1.5)
                new_bal = add_points(ctx.author.id, profit)
                embed   = result_embed(
                    "🃏 Blackjack Naturel ! 🎉", won=True,
                    bet=bet, profit=profit, new_bal=new_bal,
                    description=hand_str(player)
                )
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                return

            def reaction_check(r, u):
                return (u == ctx.author
                        and r.message.id == msg.id
                        and str(r.emoji) in ("🇭", "🇸", "🇩"))

            # ── tour du joueur ───────────────────────────────────────────
            current_bet = bet
            while hand_total(player) < 21:
                try:
                    reaction, _ = await self.bot.wait_for(
                        "reaction_add", timeout=30.0, check=reaction_check
                    )
                    await msg.remove_reaction(reaction.emoji, ctx.author)
                except asyncio.TimeoutError:
                    break   # stand automatique

                emoji = str(reaction.emoji)

                if emoji == "🇭":
                    player.append(deck.pop())
                    await msg.edit(embed=make_embed(player, dealer))
                    if hand_total(player) > 21:
                        break

                elif emoji == "🇸":
                    break

                elif emoji == "🇩" and len(player) == 2:
                    if current_bet * 2 > get_points(ctx.author.id) + current_bet:
                        await ctx.send("❌ Solde insuffisant pour doubler.", delete_after=5)
                    else:
                        current_bet *= 2
                        player.append(deck.pop())
                        await msg.edit(embed=make_embed(player, dealer,
                                                        title=f"🃏 Blackjack — Double ({fmt(current_bet)} pts)"))
                        break

            # ── tour du croupier ─────────────────────────────────────────
            pt = hand_total(player)
            if pt <= 21:
                while hand_total(dealer) < 17:
                    dealer.append(deck.pop())
                    await msg.edit(embed=make_embed(player, dealer, reveal=True,
                                                    title="🃏 Blackjack — Tour du croupier"))
                    await asyncio.sleep(1)

            # ── résultat ─────────────────────────────────────────────────
            dt = hand_total(dealer)

            if pt > 21:
                result_title, won, profit = "🃏 Bust ! Défaite", False, -current_bet
            elif dt > 21:
                result_title, won, profit = "🃏 Croupier Bust ! Victoire", True, current_bet
            elif pt > dt:
                result_title, won, profit = "🃏 Victoire !", True, current_bet
            elif pt < dt:
                result_title, won, profit = "🃏 Défaite", False, -current_bet
            else:
                result_title, won, profit = "🃏 Égalité — Mise remboursée", True, 0

            new_bal = add_points(ctx.author.id, profit)
            embed   = result_embed(
                result_title, won=won,
                bet=current_bet, profit=profit, new_bal=new_bal,
                description=(
                    f"🎴 **Vous ({pt})** : {hand_str(player)}\n"
                    f"🎭 **Croupier ({dt})** : {hand_str(dealer)}"
                )
            )
            await msg.edit(embed=embed)
            await msg.clear_reactions()

        finally:
            self._unlock(ctx.author.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  CRASH
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="crash")
    async def crash(self, ctx, bet: int = None):
        """Jeu Crash — encaissez avant le crash. Usage : `j!crash <mise>`"""
        if not await check_bet(ctx, bet):
            return

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return

        try:
            # point de crash : distribution exponentielle biaisée vers le bas
            crash_point = round(random.uniform(1.01, 20.0) * random.choice([1, 1, 1, 0.3]), 2)
            crash_point = max(1.01, crash_point)

            multiplier  = 1.00
            cashed_out  = False

            def make_embed(mult: float, potential: float) -> discord.Embed:
                if mult < 1.5:    color = 0x2ecc71
                elif mult < 3:    color = 0xf39c12
                elif mult < 7:    color = 0xe67e22
                else:             color = 0xe74c3c
                bars = min(20, int(mult * 2))
                graph = "🟩" * bars + "⬜" * (20 - bars)
                embed = discord.Embed(title="🚀 Crash Game", color=color)
                embed.add_field(name="📈 Multiplicateur", value=f"**{mult:.2f}x**", inline=True)
                embed.add_field(name="💰 Gain potentiel", value=f"{fmt(potential)} pts", inline=True)
                embed.add_field(name="📊", value=graph, inline=False)
                embed.set_footer(text="Réagissez 💰 pour encaisser !")
                return embed

            msg = await ctx.send(embed=make_embed(multiplier, bet))
            await msg.add_reaction("💰")

            def cashout_check(r, u):
                return (u == ctx.author
                        and r.message.id == msg.id
                        and str(r.emoji) == "💰")

            while multiplier < crash_point:
                # incrément progressif
                if multiplier < 2:    inc = 0.05
                elif multiplier < 5:  inc = 0.10
                elif multiplier < 10: inc = 0.20
                else:                 inc = 0.50

                multiplier = round(multiplier + inc, 2)
                potential  = int(bet * multiplier)

                await msg.edit(embed=make_embed(multiplier, potential))

                try:
                    await self.bot.wait_for("reaction_add", timeout=0.4, check=cashout_check)
                    cashed_out = True
                    break
                except asyncio.TimeoutError:
                    pass

            await msg.clear_reactions()

            if cashed_out:
                gross   = int(bet * multiplier)
                profit  = gross - bet
                new_bal = add_points(ctx.author.id, profit)
                embed   = result_embed(
                    f"💰 Encaissé à {multiplier:.2f}x !",
                    won=True, bet=bet, profit=profit, new_bal=new_bal,
                    description=f"Crash survenu à **{crash_point:.2f}x** — bien joué !"
                )
            else:
                profit  = -bet
                new_bal = add_points(ctx.author.id, profit)
                embed   = result_embed(
                    f"💥 Crash à {crash_point:.2f}x !",
                    won=False, bet=bet, profit=profit, new_bal=new_bal,
                    description="Tu n'as pas encaissé à temps."
                )

            await msg.edit(embed=embed)

        finally:
            self._unlock(ctx.author.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  ROULETTE
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="roulette")
    async def roulette(self, ctx, bet: int = None, *, choice: str = None):
        """
        Roulette européenne. Usage : `j!roulette <mise> <pari>`
        Paris : numéro (0-36) · rouge/noir · pair/impair · 1-18/19-36
        """
        if not await check_bet(ctx, bet):
            return

        if choice is None:
            embed = discord.Embed(
                title="🎡 Roulette — Aide",
                color=0x8b0000,
                description=(
                    "**Usage :** `j!roulette <mise> <pari>`\n\n"
                    "**Paris disponibles :**\n"
                    "• Numéro : `0` à `36` — gain **x36**\n"
                    "• Couleur : `rouge` / `noir` — gain **x2**\n"
                    "• Parité : `pair` / `impair` — gain **x2**\n"
                    "• Moitié : `1-18` / `19-36` — gain **x2**"
                )
            )
            await ctx.send(embed=embed)
            return

        choice = choice.lower().strip()

        # validation du pari
        if choice.isdigit() and 0 <= int(choice) <= 36:
            bet_type, display = "number", f"numéro {choice}"
        elif choice in ("rouge", "red", "r"):
            bet_type, choice, display = "red",    "rouge",  "rouge 🔴"
        elif choice in ("noir", "black", "b"):
            bet_type, choice, display = "black",  "noir",   "noir ⚫"
        elif choice in ("pair", "even", "e"):
            bet_type, choice, display = "even",   "pair",   "pair"
        elif choice in ("impair", "odd", "o"):
            bet_type, choice, display = "odd",    "impair", "impair"
        elif choice in ("1-18", "bas", "low"):
            bet_type, choice, display = "low",    "1-18",   "1-18"
        elif choice in ("19-36", "haut", "high"):
            bet_type, choice, display = "high",   "19-36",  "19-36"
        else:
            await ctx.send("❌ Pari invalide. Fais `j!roulette` sans argument pour l'aide.", delete_after=8)
            return

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return

        try:
            msg = await ctx.send(embed=discord.Embed(
                title="🎡 Roulette — La roue tourne…",
                description=f"Paris : **{display}**",
                color=0x8b0000
            ))

            # animation
            for i in range(8):
                await msg.edit(embed=discord.Embed(
                    title="🎡 Roulette — " + "🌀" * ((i % 3) + 1),
                    description=f"Paris : **{display}**",
                    color=0x8b0000
                ))
                await asyncio.sleep(0.35 + i * 0.05)

            # tirage
            number = random.randint(0, 36)

            if number == 0:
                color_str, color_emoji = "vert", "🟢"
            elif number in ROULETTE_RED:
                color_str, color_emoji = "rouge", "🔴"
            else:
                color_str, color_emoji = "noir", "⚫"

            # vérification du gain
            if bet_type == "number":
                won = (int(choice) == number)
                multiplier = 36
            elif bet_type == "red":
                won, multiplier = (number in ROULETTE_RED), 2
            elif bet_type == "black":
                won, multiplier = (number in ROULETTE_BLACK), 2
            elif bet_type == "even":
                won, multiplier = (number != 0 and number % 2 == 0), 2
            elif bet_type == "odd":
                won, multiplier = (number != 0 and number % 2 == 1), 2
            elif bet_type == "low":
                won, multiplier = (1 <= number <= 18), 2
            else:  # high
                won, multiplier = (19 <= number <= 36), 2

            profit  = bet * (multiplier - 1) if won else -bet
            new_bal = add_points(ctx.author.id, profit)

            embed = result_embed(
                title="🎡 Roulette — " + ("Victoire !" if won else "Défaite"),
                won=won, bet=bet, profit=profit, new_bal=new_bal,
                description=(
                    f"La bille s'arrête sur **{number}** {color_emoji} {color_str}\n"
                    f"Ton pari : **{display}**"
                )
            )
            await msg.edit(embed=embed)

        finally:
            self._unlock(ctx.author.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  MINES
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="mines", aliases=["mine", "minesweeper"])
    async def mines(self, ctx, bet: int = None, num_mines: int = 3):
        """
        Champ de mines 5×5. Usage : `j!mines <mise> [nb_mines]`
        Tapez un numéro 1-25 pour creuser, ou `cash` pour encaisser.
        """
        if not await check_bet(ctx, bet):
            return

        if not 1 <= num_mines <= 20:
            await ctx.send("❌ Nombre de mines : entre 1 et 20.", delete_after=8)
            return

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return

        try:
            mines      = set(random.sample(range(25), num_mines))
            revealed   = set()
            game_over  = False

            def multiplier_now() -> float:
                gems = len([c for c in revealed if c not in mines])
                if gems == 0:
                    return 1.0
                return round(1.0 + gems * num_mines * 0.25, 2)

            def grid_display() -> str:
                rows = []
                for row in range(5):
                    line = ""
                    for col in range(5):
                        pos = row * 5 + col
                        if pos in revealed:
                            line += "💎 " if pos not in mines else "💥 "
                        else:
                            num_str = str(pos + 1).zfill(2)
                            line += f"`{num_str}` "
                    rows.append(line)
                return "\n".join(rows)

            def make_embed(title: str = "💣 Mines", color: int = 0x8b4513) -> discord.Embed:
                gems  = len([c for c in revealed if c not in mines])
                mult  = multiplier_now()
                embed = discord.Embed(title=title, color=color)
                embed.description = grid_display()
                embed.add_field(name="💎 Gemmes",       value=str(gems),                 inline=True)
                embed.add_field(name="📈 Multiplicateur", value=f"{mult:.2f}x",           inline=True)
                embed.add_field(name="💰 Gain potentiel", value=f"{fmt(int(bet * mult))} pts", inline=True)
                embed.set_footer(text="Tapez un numéro (1-25) pour creuser · 'cash' pour encaisser")
                return embed

            msg = await ctx.send(embed=make_embed())

            def msg_check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            while not game_over:
                try:
                    response = await self.bot.wait_for("message", timeout=90.0, check=msg_check)
                    try:
                        await response.delete()
                    except discord.Forbidden:
                        pass

                    content = response.content.strip().lower()

                    # ── cash out ─────────────────────────────────────────
                    if content == "cash":
                        gems = len([c for c in revealed if c not in mines])
                        if gems == 0:
                            await ctx.send("❌ Creuse au moins une gemme avant d'encaisser !", delete_after=5)
                            continue
                        mult    = multiplier_now()
                        gross   = int(bet * mult)
                        profit  = gross - bet
                        new_bal = add_points(ctx.author.id, profit)
                        embed   = result_embed(
                            f"💰 Encaissé à {mult:.2f}x !",
                            won=True, bet=bet, profit=profit, new_bal=new_bal,
                            description=grid_display()
                        )
                        await msg.edit(embed=embed)
                        game_over = True

                    # ── creuser ──────────────────────────────────────────
                    elif content.isdigit():
                        pos = int(content) - 1
                        if not 0 <= pos <= 24:
                            await ctx.send("❌ Numéro invalide (1-25).", delete_after=4)
                            continue
                        if pos in revealed:
                            await ctx.send("❌ Case déjà révélée.", delete_after=4)
                            continue

                        revealed.add(pos)

                        if pos in mines:
                            # révèle tout
                            revealed.update(range(25))
                            profit  = -bet
                            new_bal = add_points(ctx.author.id, profit)
                            embed   = result_embed(
                                "💥 Mine ! Défaite",
                                won=False, bet=bet, profit=profit, new_bal=new_bal,
                                description=grid_display()
                            )
                            await msg.edit(embed=embed)
                            game_over = True

                        else:
                            # victoire parfaite ?
                            safe = [i for i in range(25) if i not in mines]
                            if all(s in revealed for s in safe):
                                mult    = multiplier_now() + 1.0   # bonus
                                gross   = int(bet * mult)
                                profit  = gross - bet
                                new_bal = add_points(ctx.author.id, profit)
                                embed   = result_embed(
                                    "🏆 Victoire Parfaite !",
                                    won=True, bet=bet, profit=profit, new_bal=new_bal,
                                    description=grid_display()
                                )
                                await msg.edit(embed=embed)
                                game_over = True
                            else:
                                await msg.edit(embed=make_embed())

                    else:
                        await ctx.send("❌ Tape un numéro (1-25) ou `cash`.", delete_after=4)

                except asyncio.TimeoutError:
                    gems = len([c for c in revealed if c not in mines])
                    if gems > 0:
                        mult    = multiplier_now()
                        gross   = int(bet * mult)
                        profit  = gross - bet
                        new_bal = add_points(ctx.author.id, profit)
                        embed   = result_embed(
                            "⏰ Temps écoulé — Auto cash-out",
                            won=True, bet=bet, profit=profit, new_bal=new_bal,
                            description=grid_display()
                        )
                    else:
                        profit  = -bet
                        new_bal = add_points(ctx.author.id, profit)
                        embed   = result_embed(
                            "⏰ Temps écoulé — Défaite",
                            won=False, bet=bet, profit=profit, new_bal=new_bal,
                            description=grid_display()
                        )
                    await msg.edit(embed=embed)
                    game_over = True

        finally:
            self._unlock(ctx.author.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  ROUE DE LA FORTUNE
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="wheel", aliases=["roue", "fortune"])
    async def wheel(self, ctx, bet: int = None):
        """Roue de la Fortune. Usage : `j!wheel <mise>`"""
        if not await check_bet(ctx, bet):
            return

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return

        try:
            segments_display = "  ".join(s["label"] for s in WHEEL_SEGMENTS)
            embed = discord.Embed(
                title="🎡 Roue de la Fortune",
                description=f"{segments_display}\n\nRéagissez 🎲 pour lancer !",
                color=0xffd700
            )
            embed.add_field(name="💰 Mise", value=f"{fmt(bet)} pts", inline=True)
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("🎲")

            def spin_check(r, u):
                return (u == ctx.author
                        and r.message.id == msg.id
                        and str(r.emoji) == "🎲")

            try:
                await self.bot.wait_for("reaction_add", timeout=30.0, check=spin_check)
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(
                    title="⏰ Temps écoulé",
                    description="La mise est remboursée.",
                    color=0x95a5a6
                ))
                await msg.clear_reactions()
                return

            await msg.clear_reactions()

            # animation
            for i in range(14):
                fake = random.choice(WHEEL_SEGMENTS)
                await msg.edit(embed=discord.Embed(
                    title="🎡 La roue tourne…",
                    description=f"**{fake['label']}**",
                    color=0xffd700
                ))
                await asyncio.sleep(0.15 + i * 0.06)

            # tirage pondéré
            total_weight = sum(s["weight"] for s in WHEEL_SEGMENTS)
            pick = random.uniform(0, total_weight)
            cumul = 0
            segment = WHEEL_SEGMENTS[-1]
            for s in WHEEL_SEGMENTS:
                cumul += s["weight"]
                if pick <= cumul:
                    segment = s
                    break

            multiplier = segment["multiplier"]
            gross      = int(bet * multiplier)
            profit     = gross - bet
            new_bal    = add_points(ctx.author.id, profit)
            won        = profit >= 0

            embed = result_embed(
                title="🎡 Roue — " + ("Victoire !" if won else "Défaite"),
                won=won, bet=bet, profit=profit, new_bal=new_bal,
                description=f"La roue s'arrête sur **{segment['label']}**"
            )
            await msg.edit(embed=embed)

        finally:
            self._unlock(ctx.author.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  DUEL (PvP)
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="duel")
    async def duel(self, ctx, opponent: discord.Member = None, bet: int = None):
        """
        Duel PvP — Dé à 6 faces. Usage : `j!duel @adversaire <mise>`
        L'adversaire doit accepter en réagissant ✅.
        """
        if opponent is None or bet is None:
            await ctx.send("❌ Usage : `j!duel @adversaire <mise>`", delete_after=8)
            return
        if opponent.bot or opponent == ctx.author:
            await ctx.send("❌ Adversaire invalide.", delete_after=8)
            return
        if bet < MIN_BET:
            await ctx.send(f"❌ Mise minimum : {MIN_BET} pts.", delete_after=8)
            return
        if get_points(ctx.author.id) < bet:
            await ctx.send("❌ Solde insuffisant.", delete_after=8)
            return
        if get_points(opponent.id) < bet:
            await ctx.send(f"❌ {opponent.display_name} n'a pas assez de points.", delete_after=8)
            return

        if not self._lock(ctx.author.id):
            await ctx.send("❌ Tu as déjà un jeu en cours !", delete_after=8)
            return
        if not self._lock(opponent.id):
            self._unlock(ctx.author.id)
            await ctx.send(f"❌ {opponent.display_name} a déjà un jeu en cours !", delete_after=8)
            return

        try:
            embed = discord.Embed(
                title="⚔️ Duel !",
                description=(
                    f"{ctx.author.mention} défie {opponent.mention} pour **{fmt(bet)} pts** !\n\n"
                    f"{opponent.mention}, réagissez ✅ pour accepter ou ❌ pour refuser."
                ),
                color=0x9b59b6
            )
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")

            def accept_check(r, u):
                return (u == opponent
                        and r.message.id == msg.id
                        and str(r.emoji) in ("✅", "❌"))

            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=accept_check)
            except asyncio.TimeoutError:
                await msg.edit(embed=discord.Embed(
                    title="⏰ Duel expiré",
                    description=f"{opponent.display_name} n'a pas répondu.",
                    color=0x95a5a6
                ))
                await msg.clear_reactions()
                return

            await msg.clear_reactions()

            if str(reaction.emoji) == "❌":
                await msg.edit(embed=discord.Embed(
                    title="❌ Duel refusé",
                    description=f"{opponent.display_name} a décliné le duel.",
                    color=0xe74c3c
                ))
                return

            # ── lancer les dés ───────────────────────────────────────────
            await msg.edit(embed=discord.Embed(
                title="⚔️ Duel en cours…",
                description="Les dés roulent !",
                color=0x9b59b6
            ))
            await asyncio.sleep(1.5)

            roll_a = random.randint(1, 6)
            roll_b = random.randint(1, 6)

            # relance automatique si égalité
            rerolls = 0
            while roll_a == roll_b and rerolls < 5:
                roll_a = random.randint(1, 6)
                roll_b = random.randint(1, 6)
                rerolls += 1

            if roll_a > roll_b:
                winner, loser = ctx.author, opponent
                w_roll, l_roll = roll_a, roll_b
            elif roll_b > roll_a:
                winner, loser = opponent, ctx.author
                w_roll, l_roll = roll_b, roll_a
            else:
                # égalité parfaite → remboursement
                embed = discord.Embed(
                    title="⚔️ Duel — Égalité !",
                    description=(
                        f"🎲 {ctx.author.display_name} : **{roll_a}**\n"
                        f"🎲 {opponent.display_name} : **{roll_b}**\n\n"
                        "Mise remboursée."
                    ),
                    color=0xffd700
                )
                await msg.edit(embed=embed)
                return

            add_points(winner.id,  bet)
            add_points(loser.id,  -bet)

            embed = discord.Embed(
                title="⚔️ Duel — Résultat !",
                description=(
                    f"🎲 {ctx.author.display_name} : **{roll_a}**\n"
                    f"🎲 {opponent.display_name} : **{roll_b}**\n\n"
                    f"🏆 **{winner.display_name}** remporte **{fmt(bet)} pts** !"
                ),
                color=0x2ecc71
            )
            embed.add_field(
                name=f"💳 Solde {winner.display_name}",
                value=f"{fmt(get_points(winner.id))} pts",
                inline=True
            )
            embed.add_field(
                name=f"💳 Solde {loser.display_name}",
                value=f"{fmt(get_points(loser.id))} pts",
                inline=True
            )
            await msg.edit(embed=embed)

        finally:
            self._unlock(ctx.author.id)
            self._unlock(opponent.id)

    # ═══════════════════════════════════════════════════════════════════════
    #  STATS & LEADERBOARD
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="balance", aliases=["bal", "solde", "points"])
    async def balance(self, ctx, user: discord.Member = None):
        """Affiche le solde d'un joueur. Usage : `j!balance [@joueur]`"""
        target = user or ctx.author
        pts    = get_points(target.id)
        embed  = discord.Embed(
            title=f"💳 Solde — {target.display_name}",
            description=f"**{fmt(pts)} points**",
            color=0x3498db
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="ctop", aliases=["cclassement", "crich"])
    async def ctop(self, ctx):
        """Classement des joueurs les plus riches."""
        data = load_data()
        if not data:
            await ctx.send("Aucune donnée disponible.", delete_after=8)
            return

        sorted_users = sorted(data.items(), key=lambda x: x[1].get("points", 0), reverse=True)

        embed = discord.Embed(title="🏆 Classement — Top richesse", color=0xffd700)
        embed.timestamp = datetime.now()

        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 17
        lines  = []

        for i, (uid, udata) in enumerate(sorted_users[:10]):
            try:
                user = self.bot.get_user(int(uid)) or await self.bot.fetch_user(int(uid))
                name = user.display_name
            except Exception:
                name = f"Joueur #{uid[:6]}"
            pts = udata.get("points", 0)
            lines.append(f"{medals[i]} **{name}** — {fmt(pts)} pts")

        embed.description = "\n".join(lines) or "Aucun joueur."

        # position du demandeur
        for i, (uid, _) in enumerate(sorted_users):
            if uid == str(ctx.author.id):
                embed.set_footer(text=f"Ta position : #{i + 1}")
                break

        await ctx.send(embed=embed)

    # ═══════════════════════════════════════════════════════════════════════
    #  AIDE CASINO
    # ═══════════════════════════════════════════════════════════════════════

    @commands.command(name="casino")
    async def casino_help(self, ctx):
        """Liste tous les jeux du casino."""
        embed = discord.Embed(
            title="🎰 Casino — Commandes",
            color=0xe91e63,
            description=f"Préfixe : `j!`  •  Mise minimum : **{MIN_BET} pts**"
        )
        games = [
            ("🪙 coinflip <mise> <pile|face>", "Pile ou face — x2"),
            ("🎰 slot <mise>",                 "Machine à sous — jusqu'à x50"),
            ("🃏 blackjack <mise>",            "Blackjack interactif — x2 / bj x2.5"),
            ("🚀 crash <mise>",               "Crash — encaissez avant le crash"),
            ("🎡 roulette <mise> <pari>",      "Roulette européenne — jusqu'à x36"),
            ("💣 mines <mise> [mines]",         "Champ de mines 5×5 — multiplicateur croissant"),
            ("🎡 wheel <mise>",               "Roue de la Fortune — jusqu'à x25"),
            ("⚔️ duel @user <mise>",           "Duel PvP — dé à 6 faces"),
        ]
        for name, desc in games:
            embed.add_field(name=f"`j!{name}`", value=desc, inline=False)
        embed.add_field(name="\u200b", value="`j!balance` · `j!ctop`", inline=False)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Casino(bot))