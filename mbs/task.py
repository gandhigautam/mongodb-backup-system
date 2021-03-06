__author__ = 'abdul'


from date_utils import date_now
from base import MBSObject

from globals import *
###############################################################################
# CONSTANTS
###############################################################################
EVENT_STATE_CHANGE = "STATE_CHANGE"

###############################################################################
# MBSTask
###############################################################################
class MBSTask(MBSObject):
    def __init__(self):
        MBSObject.__init__(self)
        # init fields

        self._created_date = None
        self._description = None
        self._state = None
        self._engine_guid = None
        self._strategy = None
        self._logs = []
        self._start_date = None
        self._end_date = None
        self._tags = None
        self._try_count = 0
        self._priority = Priority.LOW
        self._queue_latency_in_minutes = None
        self._log_target_reference = None
        self._next_retry_date = None
        self._final_retry_date = None
        self._worker_info = None

    ###########################################################################
    def execute(self):
        """
            Abstract method. Should be implemented by sub classes
        """

    ###########################################################################
    def cleanup(self):
        """
            Abstract method. Should be implemented by sub classes
        """

    ###########################################################################
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = str(id)

    ###########################################################################
    @property
    def created_date(self):
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        self._created_date = created_date

    ###########################################################################
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    ###########################################################################
    def change_state(self, state, message=None):
        """
        Updates the state and logs a state change event
        """
        if state != self.state:
            self.state = state
            return self.log_event(name=EVENT_STATE_CHANGE, message=message)

    ###########################################################################
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    ###########################################################################
    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy

    ###########################################################################
    @property
    def engine_guid(self):
        return self._engine_guid

    @engine_guid.setter
    def engine_guid(self, engine_guid):
        self._engine_guid = engine_guid

    ###########################################################################
    @property
    def logs(self):
        return self._logs

    @logs.setter
    def logs(self, logs):
        self._logs = logs

    ###########################################################################
    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        self._start_date = start_date

    ###########################################################################
    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, end_date):
        self._end_date = end_date

    ###########################################################################
    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags):
        self._tags = tags

    ###########################################################################
    def get_tag(self, name):
        if self.tags:
            return self.tags.get(name)

    ###########################################################################
    @property
    def try_count(self):
        return self._try_count

    @try_count.setter
    def try_count(self, try_count):
        self._try_count = try_count

    ###########################################################################
    @property
    def next_retry_date(self):
        return self._next_retry_date

    @next_retry_date.setter
    def next_retry_date(self, next_retry_date):
        self._next_retry_date = next_retry_date

    ###########################################################################
    @property
    def final_retry_date(self):
        return self._final_retry_date

    @final_retry_date.setter
    def final_retry_date(self, val):
        self._final_retry_date = val

    ###########################################################################
    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, val):
        self._priority = val

    ###########################################################################
    @property
    def queue_latency_in_minutes(self):
        return self._queue_latency_in_minutes

    @queue_latency_in_minutes.setter
    def queue_latency_in_minutes(self, val):
        self._queue_latency_in_minutes = val

    ###########################################################################
    @property
    def log_target_reference(self):
        return self._log_target_reference


    @log_target_reference.setter
    def log_target_reference(self, target_reference):
        self._log_target_reference = target_reference

    ###########################################################################
    @property
    def worker_info(self):
        return self._worker_info

    @worker_info.setter
    def worker_info(self, val):
        self._worker_info = val

    ###########################################################################
    def log_event(self, event_type=EventType.INFO, name=None, message=None,
                  details=None, error_code=None):
        logs = self.logs

        log_entry = EventLogEntry()
        log_entry.event_type = event_type
        log_entry.name = name
        log_entry.date = date_now()
        log_entry.state = self.state
        log_entry.message = message
        log_entry.details = details
        log_entry.error_code = error_code

        logs.append(log_entry)
        self.logs = logs
        return log_entry


    ###########################################################################
    def exceeded_max_tries(self):
        return self.final_retry_date and (date_now() > self.final_retry_date
                                          or self.next_retry_date is None)

    ###########################################################################
    def succeeded_after_failure(self):
        return self.state == State.SUCCEEDED and self.has_failed()

    ###########################################################################
    def has_errors(self):
        return len(self.get_error_logs()) > 0

    ###########################################################################
    def has_failed(self):
        if self.logs:
            failures = filter(lambda l: l.state == State.FAILED, self.logs)
            return failures and len(failures) > 0

    ###########################################################################
    def has_warnings(self):
        return len(self.get_warning_logs()) > 0

    ###########################################################################
    def get_error_logs(self):
        return self._get_logs_by_event_type(EventType.ERROR)

    ###########################################################################
    def get_warning_logs(self):
        return self._get_logs_by_event_type(EventType.WARNING)

    ###########################################################################
    def get_info_logs(self):
        return self._get_logs_by_event_type(EventType.INFO)

    ###########################################################################
    def get_last_log_message(self):
        if self.logs:
            return self.logs[-1].message

    ###########################################################################
    def get_last_error(self):
        errors = self.get_error_logs()
        if(errors):
            return errors[-1].error_code

    ###########################################################################
    def get_last_scheduled_date(self):
        scheduled_events = filter(lambda entry: (entry.name == EVENT_STATE_CHANGE and
                                                 entry.state == State.SCHEDULED),
                                  self.logs)
        if scheduled_events:
            return scheduled_events[-1].date

    ###########################################################################
    def _get_logs_by_event_type(self, event_type):
        return filter(lambda entry: entry.event_type == event_type, self.logs)

    ###########################################################################
    def _get_logs_by_event_name(self, event_name):
        return filter(lambda entry: entry.name == event_name, self.logs)

    ###########################################################################
    def is_event_logged(self, event_name):
        """
            Accepts an event name
            Returns true if logs contain an event with the specified
            event_name

        """
        return self.event_logged_count(event_name) > 0

    ###########################################################################
    def event_logged_count(self, event_name):
        logs = filter(lambda entry: entry.name == event_name, self.logs)
        return len(logs)

    ###########################################################################
    def get_last_event_entry(self, event_name):
        if self.logs:
            event_logs = self._get_logs_by_event_name(event_name)
            if event_logs:
                return event_logs[-1]

    ###########################################################################
    def _get_state_set_date(self, state):
        """
           Returns the date of when the backup was set to the specified state.
           None if state was never set
        """

        state_logs = filter(lambda entry: entry.state == state, self.logs)
        if state_logs:
            return state_logs[0].date

    ###########################################################################
    def to_document(self, display_only=False):

        doc = super(MBSTask, self).to_document(display_only=display_only)

        doc.update({
            "_type": "BackupEngineTask",
            "createdDate": self.created_date,
            "state": self.state,
            "strategy": self.strategy and self.strategy.to_document(display_only=display_only),
            "startDate": self.start_date,
            "endDate": self.end_date,
            "engineGuid": self.engine_guid,
            "logs": self.export_logs(),
            "tryCount": self.try_count,
            "nextRetryDate": self.next_retry_date,
            "finalRetryDate": self.final_retry_date
        })

        if self.description:
            doc["description"] = self.description

        if self.tags:
            doc["tags"] = self._export_tags()

        if self.priority is not None:
            doc["priority"] = self.priority

        if self.queue_latency_in_minutes is not None:
            doc["queueLatencyInMinutes"] = self.queue_latency_in_minutes

        if self.log_target_reference:
            doc["logTargetReference"] = self.log_target_reference.to_document(display_only=display_only)

        if self.worker_info:
            doc["workerInfo"] = self.worker_info

        return doc

    ###########################################################################
    def export_logs(self, event_type=None):
        result = []
        logs = self.logs
        if event_type:
            logs = self._get_logs_by_event_type(event_type=event_type)

        for log_entry in logs:
            result.append(log_entry.to_document())

        return result

    ###########################################################################
    def _export_tags(self):
        if self.tags:
            exported_tags = {}
            for name,value in self.tags.items():
                if isinstance(value, MBSObject):
                    exported_tags[name]= value.to_document()
                else:
                    exported_tags[name] = value

            return exported_tags


###############################################################################
# EventLogEntry
###############################################################################
class EventLogEntry(MBSObject):

    ###########################################################################
    def __init__(self):
        self._event_type = None
        self._name = None
        self._date = None
        self._state = None
        self._message = None
        self._details = None
        self._error_code = None

    ###########################################################################
    @property
    def event_type(self):
        return self._event_type

    @event_type.setter
    def event_type(self, value):
        self._event_type = value

    ###########################################################################
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    ###########################################################################
    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    ###########################################################################
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    ###########################################################################
    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value

    ###########################################################################
    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    ###########################################################################
    @property
    def error_code(self):
        return self._error_code

    @error_code.setter
    def error_code(self, value):
        self._error_code = value

    ###########################################################################
    def to_document(self, display_only=False):
        doc = {
            "_type": "EventLogEntry",
            "eventType": self.event_type,
            "date": self.date,
            "state": self.state
        }
        if self.name:
            doc["name"] = self.name

        if self.message:
            doc["message"] = self.message

        if self.details:
            doc["details"] = self.details

        if self.error_code:
            doc["errorCode"] = self.error_code.to_document(display_only=display_only)

        return doc


###############################################################################
# Helpers
###############################################################################
def state_change_log_entry(state, message=None):

    log_entry = EventLogEntry()
    log_entry.event_type = EventType.INFO
    log_entry.name = EVENT_STATE_CHANGE
    log_entry.date = date_now()
    log_entry.state = state
    log_entry.message = message


    return log_entry
