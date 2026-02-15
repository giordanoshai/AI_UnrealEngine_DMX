import sys
import os
import logging
from aetherlight.database import database, auth_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_database():
    logger.info("Verifying Database CRUD...")
    
    # 1. Create Project
    project = database.create_project(
        project_name="Verification Project",
        fixtures=[],
        user_id="local-user"
    )
    if not project:
        logger.error("❌ Failed to create project")
        return False
    logger.info(f"✅ Created project: {project['id']}")
    
    # 2. Get Project
    fetched_project = database.get_project(project_id=project['id'])
    if not fetched_project:
        logger.error("❌ Failed to get project")
        return False
    logger.info(f"✅ Fetched project: {fetched_project['project_name']}")
    
    # 3. List Projects
    projects = database.list_projects()
    if len(projects) == 0:
        logger.error("❌ Failed to list projects")
        return False
    logger.info(f"✅ Listed {len(projects)} projects")
    
    # 4. Create Effect
    effect = database.create_effect(
        effect_name="Test Effect",
        description="A test effect",
        primitives=[],
        duration=5.0
    )
    if not effect:
        logger.error("❌ Failed to create effect")
        return False
    logger.info(f"✅ Created effect: {effect['id']}")
    
    return True

def verify_auth():
    logger.info("Verifying Auth Manager...")
    auth = auth_manager.get_auth_manager()
    user = auth.get_current_user()
    if user['id'] != 'local-user':
        logger.error(f"❌ Unexpected user ID: {user['id']}")
        return False
    logger.info(f"✅ Current user: {user['id']}")
    return True

def verify_gui_import():
    logger.info("Verifying GUI Import...")
    try:
        from PyQt6.QtWidgets import QApplication
        from aetherlight.gui.main_window import MainWindow
        # We don't verify instantiation as it requires a running event loop and display
        logger.info("✅ Successfully imported MainWindow")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import GUI components: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Exception during GUI import: {e}")
        return False

if __name__ == "__main__":
    print("Starting Verification...")
    db_ok = verify_database()
    auth_ok = verify_auth()
    gui_ok = verify_gui_import()
    
    if db_ok and auth_ok and gui_ok:
        print("\n🎉 All verifications passed!")
        sys.exit(0)
    else:
        print("\n❌ Verification failed!")
        sys.exit(1)
