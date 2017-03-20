"""Contain the tests for proxy device server."""

# Imports
import pytest

# Tango imports
from tango.test_context import DeviceTestContext
from tango import DevState, EventType, EventData, AttrQuality
from tango import AttrWriteType, DevFailed

# Facade imports
from facadedevice import Facade, proxy_attribute, utils

# Local imports
from test_simple import event_mock


def test_proxy_attribute(mocker):

    class Test(Facade):

        attr = proxy_attribute(
            dtype=float,
            prop='prop')

    change_events, archive_events = event_mock(mocker, Test)

    mocker.patch('facadedevice.utils.DeviceProxy')
    inner_proxy = utils.DeviceProxy.return_value
    inner_proxy.dev_name.return_value = 'a/b/c'
    subscribe_event = inner_proxy.subscribe_event

    with DeviceTestContext(Test, properties={'prop': 'a/b/c/d'}) as proxy:
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check mocks
        utils.DeviceProxy.assert_called_with('a/b/c')
        assert subscribe_event.called
        cb = subscribe_event.call_args[0][2]
        args = 'd', EventType.CHANGE_EVENT, cb, [], False
        subscribe_event.assert_called_with(*args)
        # No event pushed
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()
        # Trigger events
        event = mocker.Mock(spec=EventData)
        event.attr_name = 'a/b/c/d'
        event.errors = False
        event.attr_value.value = 1.2
        event.attr_value.time.totime.return_value = 3.4
        event.attr_value.quality = AttrQuality.ATTR_ALARM
        cb(event)
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check events
        expected = 1.2, 3.4, AttrQuality.ATTR_ALARM
        change_events['attr'].assert_called_with(*expected)
        archive_events['attr'].assert_called_with(*expected)


def test_proxy_attribute_with_convertion(mocker):

    class Test(Facade):

        @proxy_attribute(
            dtype=float,
            prop='prop')
        def attr(self, raw):
            return raw*10

    change_events, archive_events = event_mock(mocker, Test)

    mocker.patch('facadedevice.utils.DeviceProxy')
    inner_proxy = utils.DeviceProxy.return_value
    inner_proxy.dev_name.return_value = 'a/b/c'
    subscribe_event = inner_proxy.subscribe_event

    with DeviceTestContext(Test, properties={'prop': 'a/b/c/d'}) as proxy:
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check mocks
        utils.DeviceProxy.assert_called_with('a/b/c')
        assert subscribe_event.called
        cb = subscribe_event.call_args[0][2]
        args = 'd', EventType.CHANGE_EVENT, cb, [], False
        subscribe_event.assert_called_with(*args)
        # No event pushed
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()
        # Trigger events
        event = mocker.Mock(spec=EventData)
        event.attr_name = 'a/b/c/d'
        event.errors = False
        event.attr_value.value = 1.2
        event.attr_value.time.totime.return_value = 3.4
        event.attr_value.quality = AttrQuality.ATTR_ALARM
        cb(event)
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check events
        expected = 12., 3.4, AttrQuality.ATTR_ALARM
        change_events['attr'].assert_called_with(*expected)
        archive_events['attr'].assert_called_with(*expected)


def test_writable_proxy_attribute(mocker):

    class Test(Facade):

        attr = proxy_attribute(
            dtype=float,
            prop='prop',
            access=AttrWriteType.READ_WRITE)

    change_events, archive_events = event_mock(mocker, Test)

    mocker.patch('facadedevice.utils.DeviceProxy')
    inner_proxy = utils.DeviceProxy.return_value
    inner_proxy.dev_name.return_value = 'a/b/c'
    subscribe_event = inner_proxy.subscribe_event

    with DeviceTestContext(Test, properties={'prop': 'a/b/c/d'}) as proxy:
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check mocks
        utils.DeviceProxy.assert_called_with('a/b/c')
        assert subscribe_event.called
        cb = subscribe_event.call_args[0][2]
        args = 'd', EventType.CHANGE_EVENT, cb, [], False
        subscribe_event.assert_called_with(*args)
        # No event pushed
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()
        # Trigger events
        event = mocker.Mock(spec=EventData)
        event.attr_name = 'a/b/c/d'
        event.errors = False
        event.attr_value.value = 1.2
        event.attr_value.time.totime.return_value = 3.4
        event.attr_value.quality = AttrQuality.ATTR_ALARM
        cb(event)
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check events
        expected = 1.2, 3.4, AttrQuality.ATTR_ALARM
        change_events['attr'].assert_called_with(*expected)
        archive_events['attr'].assert_called_with(*expected)
        # Test write
        utils.DeviceProxy.reset_mock()
        proxy.write_attribute('attr', 32.)
        utils.DeviceProxy.assert_called_with('a/b/c')
        inner_proxy.write_attribute.assert_called_with('d', 32.)


def test_proxy_attribute_with_periodic_event(mocker):

    class Test(Facade):

        attr = proxy_attribute(
            dtype=float,
            prop='prop')

    def sub(attr, etype, *args):
        if etype != EventType.PERIODIC_EVENT:
            raise DevFailed('Nope')

    change_events, archive_events = event_mock(mocker, Test)

    mocker.patch('facadedevice.utils.DeviceProxy')
    inner_proxy = utils.DeviceProxy.return_value
    inner_proxy.dev_name.return_value = 'a/b/c'
    subscribe_event = inner_proxy.subscribe_event
    subscribe_event.side_effect = sub

    with DeviceTestContext(Test, properties={'prop': 'a/b/c/d'}) as proxy:
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check mocks
        utils.DeviceProxy.assert_called_with('a/b/c')
        assert subscribe_event.called
        cb = subscribe_event.call_args[0][2]
        args = 'd', EventType.PERIODIC_EVENT, cb, [], False
        subscribe_event.assert_called_with(*args)
        # No event pushed
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()
        # Trigger events
        event = mocker.Mock(spec=EventData)
        event.attr_name = 'a/b/c/d'
        event.errors = False
        event.attr_value.value = 1.2
        event.attr_value.time.totime.return_value = 3.4
        event.attr_value.quality = AttrQuality.ATTR_ALARM
        cb(event)
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check events
        expected = 1.2, 3.4, AttrQuality.ATTR_ALARM
        change_events['attr'].assert_called_with(*expected)
        archive_events['attr'].assert_called_with(*expected)


def test_proxy_attribute_not_evented(mocker):

    class Test(Facade):

        attr = proxy_attribute(
            dtype=float,
            prop='prop')

    change_events, archive_events = event_mock(mocker, Test)

    mocker.patch('facadedevice.utils.DeviceProxy')
    inner_proxy = utils.DeviceProxy.return_value
    inner_proxy.dev_name.return_value = 'a/b/c'
    subscribe_event = inner_proxy.subscribe_event
    subscribe_event.side_effect = DevFailed

    with DeviceTestContext(Test, properties={'prop': 'a/b/c/d'}) as proxy:
        # Device in fault
        expected = "Exception while connecting proxy_attribute <attr>"
        assert proxy.state() == DevState.FAULT
        assert expected in proxy.status()
        # Check mocks
        utils.DeviceProxy.assert_called_with('a/b/c')
        assert subscribe_event.called
        cb = subscribe_event.call_args[0][2]
        args = 'd', EventType.PERIODIC_EVENT, cb, [], False
        subscribe_event.assert_called_with(*args)
        # No event pushed
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()


def test_proxy_attribute_with_wrong_events(mocker):

    class Test(Facade):

        attr = proxy_attribute(
            dtype=float,
            prop='prop')

    change_events, archive_events = event_mock(mocker, Test)

    mocker.patch('facadedevice.utils.DeviceProxy')
    inner_proxy = utils.DeviceProxy.return_value
    inner_proxy.dev_name.return_value = 'a/b/c'
    subscribe_event = inner_proxy.subscribe_event

    with DeviceTestContext(Test, properties={'prop': 'a/b/c/d'}) as proxy:
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check mocks
        utils.DeviceProxy.assert_called_with('a/b/c')
        assert subscribe_event.called
        cb = subscribe_event.call_args[0][2]
        args = 'd', EventType.CHANGE_EVENT, cb, [], False
        subscribe_event.assert_called_with(*args)
        # No event pushed
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()
        # Invalid event
        cb("Not an event")
        assert proxy.state() == DevState.UNKNOWN
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()
        # Ignore event
        event = mocker.Mock(spec=EventData)
        event.attr_name = 'a/b/c/d'
        exception = DevFailed('Ooops')
        exception.reason = 'API_PollThreadOutOfSync'
        event.errors = [exception, RuntimeError()]
        cb(event)
        assert proxy.state() == DevState.UNKNOWN
        change_events['attr'].assert_not_called()
        archive_events['attr'].assert_not_called()
        # Error event
        event = mocker.Mock(spec=EventData)
        event.attr_name = 'a/b/c/d'
        exception = DevFailed('Ooops')
        event.errors = [exception, RuntimeError()]
        cb(event)
        assert proxy.state() == DevState.UNKNOWN
        change_events['attr'].assert_called_with(exception)
        archive_events['attr'].assert_called_with(exception)


def test_disabled_proxy_attribute(mocker):

    class Test(Facade):

        attr = proxy_attribute(
            dtype=float,
            prop='prop',
            access=AttrWriteType.READ_WRITE)

    change_events, archive_events = event_mock(mocker, Test)
    device_proxy = mocker.patch('facadedevice.utils.DeviceProxy')

    with DeviceTestContext(Test, properties={'prop': 'NONE'}) as proxy:
        # Device not in fault
        assert proxy.state() == DevState.UNKNOWN
        # Check mocks
        assert not device_proxy.called
        # Test write
        with pytest.raises(DevFailed) as ctx:
            proxy.attr = 3
        # Check
        assert "This proxy command is disabled" in str(ctx.value)


def test_non_writable_proxy_attribute(mocker):

    class Test(Facade):

        attr = proxy_attribute(
            dtype=float,
            prop='prop',
            access=AttrWriteType.READ_WRITE)

    change_events, archive_events = event_mock(mocker, Test)

    mocker.patch('facadedevice.utils.DeviceProxy')
    inner_proxy = utils.DeviceProxy.return_value
    config = mocker.Mock(writable=AttrWriteType.READ)
    inner_proxy.get_attribute_config.return_value = config
    inner_proxy.dev_name.return_value = 'a/b/c'

    with DeviceTestContext(Test, properties={'prop': 'a/b/c/d'}) as proxy:
        assert proxy.state() == DevState.FAULT
        assert "The attribute a/b/c/d is not writable" in proxy.status()