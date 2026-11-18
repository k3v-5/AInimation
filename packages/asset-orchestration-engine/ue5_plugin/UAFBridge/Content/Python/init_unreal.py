"""
AOE Plugin Initialization Script for Unreal Engine 5.
Runs automatically on Unreal Editor startup when UAFBridge plugin is active.
Registers editor menu entries and tools for one-click asset ingestion and synchronization.
"""

try:
    import unreal
    IN_UNREAL = hasattr(unreal, "log") and hasattr(unreal, "ToolMenus")
except ImportError:
    unreal = None
    IN_UNREAL = False


def register_aoe_menus():
    """Registers the AOE menu in the Unreal Editor Level Editor Menu Bar."""
    if not IN_UNREAL:
        return

    unreal.log("[AOE] Initializing UAFBridge Python Integration...")

    menus = unreal.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if not main_menu:
        return

    aoe_menu = main_menu.add_sub_menu(
        owner="UAFBridge",
        section_name="",
        name="AOEMenu",
        label="AOE",
        tool_tip="Asset Orchestration Engine Tools and Automation"
    )

    # Ingest Entry
    entry = unreal.ToolMenuEntry(
        name="AOE_Ingest_Bundle",
        type=unreal.MultiBlockType.MENU_ENTRY
    )
    entry.set_label("Ingest AOE Bundle")
    entry.set_tool_tip("Automated ingestion of Nanite meshes, PBR textures, Niagara systems, and spawn actors from AOE bundle.")
    entry.set_string_command(
        type=unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string="from aoe_editor_ingest import AOEUnrealIngestionPipeline; AOEUnrealIngestionPipeline().run_pipeline()"
    )
    aoe_menu.add_menu_entry("AOE_Actions", entry)

    menus.refresh_all_widgets()
    unreal.log("[AOE] UAFBridge menu successfully registered into Unreal Editor.")


if __name__ == "__main__" or IN_UNREAL:
    register_aoe_menus()
