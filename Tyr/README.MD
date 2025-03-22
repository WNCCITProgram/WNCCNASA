# NASA Tyr the Mars Rover

Project management is at [ClickUp](https://www.clickup.com)

## Videos

- [Stair Climbing Rover Assembly](https://www.youtube.com/watch?v=bXdt8hng2WM&t=590s)
- [Stair Climbing Rover Outdoor Test](https://www.youtube.com/watch?v=90HxqwZaWRA)
- [Robot Driving on Stairs](https://www.youtube.com/watch?v=9Od0E53R8PE&list=PLDlq-eaB9UnAa4w-3D7UfHbri6fAKWdxc&index=2)
- [First Run with Onboard Camera Overlay](https://www.youtube.com/watch?v=GkBlQkr3NZU&t=14s)
- [I built a Rover using a Raspberry pi & Arduino](https://www.youtube.com/watch?v=IoCaTgmUSvc&list=WL&index=4&t=49s)
- [Six Wheeled Robot Garden Rover](https://www.youtube.com/watch?v=eMBtcPtlUhE)
- <https://revenanteagle.org/checksix/six_wheeled_robot_garden_rover/crawler.htm>

## STL Files

- <https://www.printables.com/model/194299-stair-climbing-rover>
- <https://www.printables.com/model/201813-camera-mounts-for-stair-climbing-rover>
- <https://www.printables.com/model/202779-switch-panel-for-stair-climbing-rover>
- <https://www.printables.com/model/212819-raspberry-pi-mount-for-stair-climbing-rover>

Devil Design Bright Green and Black filament

## Original Code

<https://github.com/Lukas2233/Rover-Project>

## Redesign Electronics

- Youtube posts on the I built a Rover using a Raspberry Pi and Arduino Videos. Possibe change in electronics.
  - A few tricks on the DC-DC converters...
  - For the servos, look into a BEC for an RC plane. Much smaller than the the DC-DC you used.
  - For the Brushed DC motors, the voltage isn't the problem, it's the current. If you set the max current limit to below the max the motors can take, they can "Run at any voltage" (as the H-Bridge will protect them.)
  - Also, you can just run the bridges off full voltage, but limit the max PWM to 50%, for half voltage. (The current limit would be another level of protection.)

  - Last, look into Conformal Coating for all your PCB boards to make them water proof-ish. Dialetric grease in all the connectors (LOTS OF IT) is your friend.
  - @LukasDeem 9 months ago I've had someone mention BEC before, I need to do some research on it. I would love to find ways to make my next project like this somewhat waterproof! Thanks for the ideas!
  - @OnlineObsessionista 9 months ago you mean the Adafruit 16-Channel Servo Driver?
  - You would likely have better results with a 2S lipo battery. I know the motors say 6 V but they would be fine with the 7-8.4 V of a 2S lipo, especially if you limit the PWM duty cycle. That way you could get rid of the large buck converter.
  - Scrap the massive 6V buck converter and power the motor driver directly from a 2S lipo or li-ion battery. You will only need a small 6V (maybe 3A) buck converter for the servo motors.
  - You may want to know about is Windows comes with a cool SLT util called 3D Builder which allows you to modify STL. I use it all the time. Using 3D builder you can add the camera hole and more important add needed vents.
  - You could add led to know standby , boot up and off mode Power button would be better outside And probably a charge port too.
  - Not sure what you've set the voltage in the step down converter to, but keep in mind, that with the bipolar transistors on the L298Ns H-Bridges you get a voltage drop of about 1.4V, so you might get a little more power out of your motors by increasing the voltage of the stepdown converter to 7.4V, in order to give the motors 6V, if you've not already done that. You could also check the voltage drop by measuring the voltage on one of the Outputs of your Motordrivers on fullspeed
    - Hey so yeah and some of my first outdoor test I saw that it was going super slow and I knew that I needed to up the voltage. I ended up bumping it up to 7.1v thanks for the tip on how to measure the output voltage I think I need to go back and do that and see what I'm actually getting at the output of the motor drivers.
  - you should be able to set the pi up as a AP/WIFI router. to connect the pc to directly.
  - Those L298N motor drivers are antiques though, should have gone for something much smaller!
  - I use the buck converter to drop the voltage down to 6 volts. Then I took that output and tied it into a prototyping board where I just took over a power rail on the side of the prototyping board to distribute the 6 volts. I soldered the motor power wires directly to that power rail. I'm sure there's a bad a million ways to do this better but this is how I did it.
  - Replace the voltage regulator with a LM7806.
  - About the chosen hardware: Why didn't you use a standard arduino uno with the standard arduino motor modules (4 DC motors and a few servos per modules, and they are stackable, so two should be enough) And about the voltage: Why didn't you just max out the pwm signal as an alternative to use this big step down converter? (For example: you have 6V DC motors, but a 12 V DC power source: you can directly use the 12 V, if you limit the pwm to 50%. (or 24 V with 25% max pwm).The higher voltage doesn't harm and if the total energy is the same they don't burn/overheat. As long the difference don't get to crazy (like 3V to 48V) this should work very well.)
  - are you using any kind of bearings to avoid friction between parts? and are how are you keeping the screws fastened properly at rotating parts like the "differential" gear? nyloc nuts?, 
    - No bearings, and yes I used some nylock nuts. This design would eventually wear after extended use, but I doubt I will ever run it enough for that to become a problem.
  - Can I please know how do you manage the encoders for six motors in one microcontroller Arduino Mega? 
    - So the mega offers enough pins to support them all. The only caveat here is that I was one interrupt pin short. However you can run PID algorithms without interrupts, they are just less accurate. In order to get the video done I actually didn't end up using the encoders. The are all wired up in case I change my mind!
  - But why did you use the Arduino Mega if you wanted to use a Raspberry PI? Any model from 3B could solve this task on its own, they got enough GPIOs for that purpose. Or do I miss something?.. Also if you get a good enough internet on the rover, with a little extra work you can attach a usual web-camera and have hq video with low latency using V4L. Let me know if you're interested, I can share the solution. (I was a little disappointed with the quality of PI camera so found a better option)
    - So I was worried the pi didn't have enough gpio pins. I was also thinking that it would take too much computational power to run a PID algorithm for the wheels (which I ended up cutting from scope) and the web server for the Rover control. The pi cam quality was actually good enough for me, I just wish it was a wider angle
  - i am working on the same rover using a Bluetooth module but I don't know how to connect all the motors and servo to a single Ardiuno Mega so can you please help me with it??
    - sure so the servos I connected to the digital pins. For the ground and power I soldered those wires to a common power rail on a prototyping board. For the DC motors I used h bridge motor driver boards. Those used a ton of the pwm and digital pins, but the Arduino can handle it. The only problem is if you want to use interrupts on the encoders. Since I used the SDA and SCL pins for serial communication I was one interrupt pin short. It's okay since you can use PID algorithms without interrupts.
  - I ran two servers to make my project work. One was the flask server that hosted the rover controls. The other was the server that comes with the RPi camera repo. I just ran both and pulled the camera stream over into my control website 😅
