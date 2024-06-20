import argparse

from pythonosc import dispatcher
from pythonosc import osc_server
from main import main


def some_function():
    print("Function triggered!")


def handle_osc_message(unused_addr, *args):
    print("OSC message received:", args)
    main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/trigger", handle_osc_message)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print(f"Serving on {server.server_address}")
    server.serve_forever()
