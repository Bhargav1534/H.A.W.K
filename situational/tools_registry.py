import memory.AllTools as at


TOOLS = {
    "OpenApplication": at.BasicTools.open_app,
    "AddTodoList": at.TodoListManager.add_todo,
    "SetTimer": at.BasicTools.start_timer,
    "RemoveTodoList": at.TodoListManager.remove_todo,
    "ListTodoList": at.TodoListManager.list_todos,
    "ClearTodoList": at.TodoListManager.clear_todos,
    "AddReminder": at.RemindersManager.add_reminder,
    "RemoveReminder": at.RemindersManager.delete_reminder,
    "ListReminders": at.RemindersManager.list_reminders,
    "MarkReminderAsDone": at.RemindersManager.mark_reminder_done,
    "CheckTodoList": at.TodoListManager.check_todo,
    "LockScreen": at.BasicTools.lock_system,
    "ShutdownSystem": at.BasicTools.shutdown_system,
    "RestartSystem": at.BasicTools.restart_system,
    "SetVolume": at.BasicTools.set_volume,
}
