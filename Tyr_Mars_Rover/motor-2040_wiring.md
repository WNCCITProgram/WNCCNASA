# Motor - motor2040_board Wiring

| Motor   | motor2040 board    |
|--------------- | --------------- |
| $\color{red}{\textsf{Red}}$    pwr+   | $\color{blue}{\textsf{Blue}}$   out_mot-   |
| White  pwr-   | White  out_mot+   |
| $\color{yellow}{\textsf{Yellow}}$ sig_fb   | $\color{yellow}{\textsf{Yellow}}$ encA   |
| $\color{green}{\textsf{Green}}$  sig_fb  | Black  encB  |
| $\color{blue}{\textsf{Blue}}$   enc+  | $\color{green}{\textsf{Green}}$  +3.3V  |
| Black  enc-   | $\color{red}{\textsf{Red}}$    ground  |

## In the table

- The first pair: power from 2040 to spin the motor, can be swapped (*it is in our configuration*)
- The second pair: the feedback from the motor to 2040's encoder
- The third pair: power from 2040 to the motor's encoder
