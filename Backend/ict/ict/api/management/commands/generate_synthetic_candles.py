# ict/management/commands/generate_synthetic_candles.py
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import Instrument, Candle  # adjust if your app is named differently


SYMBOLS = [
    "AAPL", "MSFT", "GOOG", "AMZN", "TSLA",
    "META", "NFLX", "NVDA", "AMD", "INTC",
    "SPY", "QQQ", "IWM", "NQ100", "ES500",
    "US30", "GC", "CL", "EURUSD", "GBPUSD",
]


class Command(BaseCommand):
    help = "Generate synthetic ICT-style intraday candles for multiple instruments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--candles-per-symbol",
            type=int,
            default=500,
            help="Number of candles per symbol (default: 500)",
        )
        parser.add_argument(
            "--timeframe",
            type=str,
            default="5m",
            help="Timeframe label (default: 5m)",
        )

    def handle(self, *args, **options):
        candles_per_symbol = options["candles_per_symbol"]
        timeframe = options["timeframe"]

        total_target = len(SYMBOLS) * candles_per_symbol
        self.stdout.write(self.style.NOTICE(
            f"Generating ~{total_target} candles for {len(SYMBOLS)} symbols..."
        ))

        for symbol in SYMBOLS:
            instrument, _ = Instrument.objects.get_or_create(
                symbol=symbol,
                defaults={"name": symbol},
            )

            self._generate_for_symbol(instrument, candles_per_symbol, timeframe)

        self.stdout.write(self.style.SUCCESS("Done generating synthetic candles."))

    def _generate_for_symbol(self, instrument, n, timeframe):
        """
        Generate n synthetic candles for a single instrument.
        We use a random walk with:
        - Volatility regimes
        - Occasional displacement candles (ICT-style)
        - Wicks for liquidity grabs
        """
        # Start some time in the past (e.g. n * 5min ago)
        minutes_per_candle = 5  # since timeframe default is '5m'
        end_time = timezone.now()
        start_time = end_time - timedelta(minutes=minutes_per_candle * n)

        # Choose a base price per symbol to make them different
        base_price = random.uniform(20, 300)
        price = base_price

        # Base volatility (how big each candle usually is)
        base_vol = random.uniform(0.2, 1.5)

        candles = []
        current_time = start_time

        for i in range(n):
            # Volatility regime: every 40 candles, do a "session push"
            session_factor = 1.0
            if i % 40 in (0, 1, 2, 3, 4):
                session_factor = 2.0  # displacement phase

            # Random walk for close
            change = random.gauss(0, base_vol * session_factor)
            o = price
            c = price + change

            # Basic high/low around open/close
            true_range = abs(change) + base_vol * session_factor
            h = max(o, c) + true_range * random.uniform(0.2, 0.8)
            l = min(o, c) - true_range * random.uniform(0.2, 0.8)

            # ICT-ish tweaks:
            # - Every 25th candle, create a big wick (liquidity grab)
            # - Every 30th candle, create a strong body (displacement candle)
            if i % 25 == 0:
                # stop run up or down
                if random.random() < 0.5:
                    h += true_range * 2.5  # big upper wick
                else:
                    l -= true_range * 2.5  # big lower wick

            if i % 30 == 0:
                # displacement body (FVG-like conditions)
                big_move = base_vol * session_factor * 4
                direction = 1 if random.random() < 0.5 else -1
                c = o + direction * big_move
                h = max(h, o, c)
                l = min(l, o, c)

            # Volume with some spikes
            vol_base = random.randint(1000, 20000)
            if i % 35 in (0, 1):
                vol_base *= random.randint(2, 5)

            candles.append(
                Candle(
                    instrument=instrument,
                    timestamp=current_time,
                    timeframe=timeframe,
                    open=round(o, 4),
                    high=round(h, 4),
                    low=round(l, 4),
                    close=round(c, 4),
                    volume=vol_base,
                )
            )

            price = c
            current_time += timedelta(minutes=minutes_per_candle)

        Candle.objects.bulk_create(candles, batch_size=1000)