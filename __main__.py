from src.core.bot import Gojo

if __name__ == "__main__":
    bot = Gojo()
    bot.__version__ = "0.0.1"
    bot.hikari_version = __import__("hikari").__version__
    bot.lightbulb_version = __import__("lightbulb").__version__
    bot.run()
