To test the forward, first check in the last row of the python file if these are the desired input.

We will use forwarder(8080,"127.0.0.1",9000, 'D') as an example for testing the decryptor. First, 
do “ncat -l 9000” in one terminal, and run forwarder.py in the second terminal, 
then “ncat -C --ssl 127.0.0.1 8080” in another terminal. We can then test our forwarder by sending 
messages in the two ncat terminals back and forth.

We will use forwarder(8080,"127.0.0.1",9000, 'E') as an example for testing the encryptor. First, 
do “ncat -l --ssl 9000” in one terminal, and run forwarder.py in the second terminal, 
then “ncat -C 127.0.0.1 8080” in another terminal. We can then test our forwarder by sending 
messages in the two ncat terminals back and forth.