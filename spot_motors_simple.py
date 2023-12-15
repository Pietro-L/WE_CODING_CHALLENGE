import sys
import bosdyn.client
import bosdyn.client.util
import bosdyn.client.lease

"""
Simple class to allow power on and power off of Boston Dynamics Spot robot. 
Created for WE Coding Challenge.
"""
class SpotMotorsSimple():

    # connect to robot
    def __init__(self):
        self._sdk = bosdyn.client.create_standard_sdk('spot-motors')
        self._robot = self._sdk.create_robot('192.168.80.3')
        self._robot.authenticate('user', 'password')
        self._lease_client = self._robot.ensure_client(bosdyn.client.lease.LeaseClient.default_service_name)
    
    # Power motors on
    def powerOn(self):
        # Check if estop triggered
        assert not self._robot.is_estopped(), 'Robot is estopped.'

        # Takes ownership of robot
        self._lease_keepalive = bosdyn.client.lease.LeaseKeepAlive(self._lease_client)
        
        # Power on robot
        self._robot.logger.info('Powering on robot... This may take several seconds.')
        self._robot.power_on(timeout_sec=20)
        assert self._robot.is_powered_on(), 'Robot power on failed.'
        self._robot.logger.info('Robot powered on.')

    # power motors off
    def powerOff(self):
        # Power off robot
        self._robot.power_off(cut_immediately=False, timeout_sec=20)
        assert not self._robot.is_powered_on(), 'Robot power off failed.'
        self._robot.logger.info('Robot safely powered off.')

        # Release ownership
        if self._lease_keepalive:
            self._lease_keepalive.shutdown()


def main():
    try:
        mySpot = SpotMotorsSimple()
        mySpot.powerOn()
        mySpot.powerOff()
        return True
    except Exception as exc:
        logger = bosdyn.client.util.get_logger()
        logger.error('Exception: %r', exc)
        return False

if __name__ == '__main__':
    if not main():
        sys.exit(1)