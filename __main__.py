import os

from core.bot import Bot

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()
    Bot().run()
