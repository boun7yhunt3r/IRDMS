from taipy.gui import Gui, State, navigate, notify, Icon

from pages.home.home_page import home_md
from pages.login_page import root
from pages.user.user_page import user_md

from utils.keycloak_manager import KeycloakManager
from utils.shepard_connect import ShepardManager
from utils.logger import logger

login_open = True
access_token = None
username = ''
password = ''
logged_in_user = ''
tree_data = []

# Initialize managers
keycloak_manager = KeycloakManager()
# shepard_manager = ShepardManager() 

menu_items = [
    ("Home", Icon("images/home.gif", "Home")),
    ("User", Icon("images/settings.gif", "User")),
]

def login(state):
    keycloak_manager.login(state)
    if state.access_token:
        logger.info(f"User successfully logged in : {state.logged_in_user}")
        shepard_manager = ShepardManager(access_token=state.access_token)
        state.tree_data = shepard_manager.build_tree_structure()
        

def logout(state):
    keycloak_manager.logout(state)

# Called when a menu item is clicked
def menu_action(state: State, var_name: str, var_value: dict):
    selected_page = var_value["args"][0]         # "Home" / "Dashboard" / "Settings"
    session_on_navigate(state, selected_page)
    navigate(state, selected_page)               # Navigate to page

def session_on_navigate(state, page_name):
    """
    Navigation handler that intercepts page navigation.
    Checks session validity before allowing navigation to protected pages.
    """
    # Allow navigation to root/initial page without session check
    if page_name in ["/", "TaiPy_root_page"]:
        return page_name
    
    # For Home page - allow navigation but check session to show/hide login dialog
    if page_name == "Home":
        if not keycloak_manager.check_session_and_logout_if_expired(state):
            state.login_open = True
        return page_name
    
    # For all other pages, require valid session
    if not keycloak_manager.check_session_and_logout_if_expired(state):
        state.login_open = True
        return "/"
    
    return page_name

pages = {
    "/": root,
    "Home": home_md,
    "User": user_md
}

if __name__ == "__main__":
    gui = Gui(pages=pages)
    gui.run(title="IRDMS", port=5005, dark_mode=True, dev_mode=True)