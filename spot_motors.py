import sys
import curses
import argparse
import bosdyn.client
import bosdyn.client.util
import bosdyn.client.lease
import bosdyn.client.estop
from bosdyn.client.robot_command import RobotCommandClient, blocking_stand, blocking_sit

"""
Class to allow power on and power off of Boston Dynamics Spot robot. 
Has integrated eStop and commands to stand or sit Spot.
Created for WE Coding Challenge.
"""
class SpotMotors():

    # connect to robot
    def __init__(self, config):

        # Set up logging based on args
        bosdyn.client.util.setup_logging(config.verbose)

        # Initialize sdk object
        self._sdk = bosdyn.client.create_standard_sdk('spot-motors')
        
        # Insert actual credentials & IP
        self._robot = self._sdk.create_robot(config.hostname)
        self._robot.authenticate('user', 'password')
        self._lease_client = self._robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
        
        # Takes ownership of robot
        self._lease_keepalive = bosdyn.client.lease.LeaseKeepAlive(self._lease_client)

        try:
            # register estop
            self._estop_client = self._robot.ensure_client(bosdyn.client.estop.EstopClient.default_service_name)
            self._estop_endpoint = bosdyn.client.estop.EstopEndpoint(self._estop_client, 'SpotMotorEstop', 9.0)
            self._estop_endpoint.force_simple_setup() 
        except:
            # estop controlled by someone else
            self._estop_client = None
            self._estop_endpoint = None

        # estop keepalive
        if self._estop_client is not None and self._estop_endpoint is not None:
            self._estop_keepalive = bosdyn.client.estop.EstopKeepAlive(self._estop_endpoint)
        else:
            self._estop_keepalive = None

    # Disengages estop        
    def eStop_Allow(self):
        self._estop_keepalive.allow()

    # Engages estop
    def eStop_Stop(self):
        self._estop_keepalive.stop()

    # Power motors on
    def powerOn(self):
        # Check if estop triggered
        assert not self._robot.is_estopped(), 'Robot is estopped.'
        
        # Power on robot
        self._robot.logger.info('Powering on robot... This may take several seconds.')
        self._robot.power_on(timeout_sec=20)
        assert self._robot.is_powered_on(), 'Robot power on failed.'
        self._robot.logger.info('Robot powered on.')

    # Power motors off
    def powerOff(self):
        # Power off robot
        self._robot.power_off(cut_immediately=False, timeout_sec=20)
        assert not self._robot.is_powered_on(), 'Robot power off failed.'
        self._robot.logger.info('Robot safely powered off.')

    # Command robot to stand
    def spotStand(self):
        assert self._robot.is_powered_on, 'Robot not powered on'
        self._robot.logger.info('Commanding robot to stand')
        command_client = self._robot.ensure_client(RobotCommandClient.default_service_name)
        blocking_stand(command_client, timeout_sec=10)
        self._robot.logger.info('Robot standing.')

    # Command robot to sit
    def spotSit(self):
        assert self._robot.is_powered_on, 'Robot not powered on'
        self._robot.logger.info('Commanding robot to sit')
        command_client = self._robot.ensure_client(RobotCommandClient.default_service_name)
        blocking_sit(command_client, timeout_sec=10)
        self._robot.logger.info('Robot sitting.')

    # Shut down class
    def shutDown(self):
        # Power off robot if on
        if self._robot.is_powered_on:
            self.powerOff()
        # Release ownership
        if self._lease_keepalive:
            self._lease_keepalive.shutdown()
        # Release estop ownership
        if self._estop_keepalive:
            self._estop_keepalive.shutdown()

def main():
    try:
        # Parse arguments for IP
        parser = argparse.ArgumentParser()
        bosdyn.client.util.add_base_arguments(parser)
        options = parser.parse_args()
        mySpot = SpotMotors(options)
        mySpot.eStop_Allow()

        stdscr = curses.initscr()
        # Clear screen
        stdscr.clear()
        # Display usage instructions in terminal
        stdscr.addstr('Running SpotMotors Class.\n')
        stdscr.addstr('\n')
        stdscr.addstr('[q]: Quit\n')
        stdscr.addstr('[SPACE]: Trigger estop\n')
        stdscr.addstr('[r]: Release estop\n')
        stdscr.addstr('[w]: Power motors on\n')
        stdscr.addstr('[e]: Power motors off\n')
        stdscr.addstr('[a]: Stand robot\n')
        stdscr.addstr('[d]: Sit robot\n')

        # Monitor estop until user exits
        while True:
            # Retrieve user input (non-blocking)
            c = stdscr.getch()
            if c == ord('q'):
                mySpot.shutDown()
                return True
            if c == ord(' '):
                mySpot.eStop_Stop()
            if c == ord('r'):
                mySpot.eStop_Allow()
            if c == ord('w'):
                mySpot.powerOn()
            if c == ord('e'):
                mySpot.powerOff()
            if c == ord('a'):
                mySpot.spotStand()
            if c == ord('d'):
                mySpot.spotSit()

    except Exception as exc:
        logger = bosdyn.client.util.get_logger()
        logger.error('Exception: %r', exc)
        return False

if __name__ == '__main__':
    if not main():
        sys.exit(1)
