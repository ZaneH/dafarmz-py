from views.submenu_view import SubmenuView


class RobotHQView(SubmenuView):
    def __init__(self, timeout=120):
        super().__init__(timeout=timeout)
