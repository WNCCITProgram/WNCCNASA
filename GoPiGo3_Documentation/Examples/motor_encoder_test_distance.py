# Import the EasyGoPiGo3 library
import easygopigo3 as easy

# Initialize a EasyGoPiGo3 object
GPG = easy.EasyGoPiGo3()

GPG.reset_encoders()
# GPG.set_speed(GPG.DEFAULT_SPEED)
# Drive forward 10 cm
GPG.drive_cm(10)

encoders_read = round(GPG.read_encoders_average())

print(f"Drove {encoders_read:.2f} cm")

if encoders_read == 10:
    print("Test passed.")
else:
    print("Test failed.")
