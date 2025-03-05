from my_serial import read_thread
from thor import Thor
from threading import Thread
from inputs import get_gamepad
import keys

thor = Thor()

read_thread.start()  # run the serial listener in a separate thread
while read_thread.is_alive():
    try:
        event = get_gamepad()[0]
    except KeyboardInterrupt:
        break
    btn = f"{event.code} {event.state}"  # event from the gamepad
    if "MSC" in btn or "SYN" in btn:
        continue
    # print(btn)
    thor.event = btn  # to maintain stop if unpressed
    match btn:
        # the moving functions run in separate threads to be able to stop on unpressed key
        case keys.L2:
            Thread(target=thor.open_claw).start()
        case keys.L1:
            Thread(target=thor.close_claw).start()
        case keys.RIGHT:
            Thread(target=thor.rotate_claw).start()
        case keys.LEFT:
            Thread(target=thor.rotate_claw_cw).start()
        case keys.DOWN:
            Thread(target=thor.move_claw_b).start()
        case keys.UP:
            Thread(target=thor.move_claw).start()
        case keys.A_2:
            Thread(target=thor.art_4).start()
        case keys.Y_4:
            Thread(target=thor.art_4_cw).start()
        case keys.B_3:
            Thread(target=thor.art_3_b).start()
        case keys.X_1:
            Thread(target=thor.art_3).start()
        case keys.R1:
            Thread(target=thor.art_2_b).start()
        case keys.R2:
            Thread(target=thor.art_2).start()
        case keys.L_AN:
            Thread(target=thor.art_1).start()
        case keys.R_AN:
            Thread(target=thor.art_1_cw).start()
        case keys.START:
            Thread(target=thor.home).start()
