package com.boatyguide;

import java.awt.event.KeyEvent;
import net.runelite.client.config.Config;
import net.runelite.client.config.ConfigGroup;
import net.runelite.client.config.ConfigItem;
import net.runelite.client.config.ConfigSection;
import net.runelite.client.config.Keybind;
import net.runelite.client.config.ModifierlessKeybind;

@ConfigGroup("boatyguide")
public interface BoatyGuideConfig extends Config
{
	@ConfigSection(
		name = "Display",
		description = "Sidebar and overlay display options",
		position = 0
	)
	String displaySection = "display";

	@ConfigSection(
		name = "Progress",
		description = "Manual progression, saved progress, and start or reset controls",
		position = 1
	)
	String progressSection = "progress";

	@ConfigSection(
		name = "Input",
		description = "Hotkeys and mouse binds for guide navigation",
		position = 2
	)
	String inputSection = "input";

	@ConfigItem(
		keyName = "contextStepCount",
		name = "Context steps",
		description = "How many upcoming steps to show beneath the current step",
		position = 0,
		section = displaySection
	)
	default int contextStepCount()
	{
		return 4;
	}

	@ConfigItem(
		keyName = "showOverlay",
		name = "Show overlay",
		description = "Show the current guide step in a small in-game overlay",
		position = 1,
		section = displaySection
	)
	default boolean showOverlay()
	{
		return true;
	}

	@ConfigItem(
		keyName = "showAdviceOverlay",
		name = "Show advice overlay",
		description = "Show a separate overlay when the current step or block has advice attached",
		position = 2,
		section = displaySection
	)
	default boolean showAdviceOverlay()
	{
		return true;
	}

	@ConfigItem(
		keyName = "showCompleteBlockButton",
		name = "Show complete block button",
		description = "Show a button in the sidebar to complete or uncomplete the current bank block",
		position = 0,
		section = progressSection
	)
	default boolean showCompleteBlockButton()
	{
		return false;
	}

	@ConfigItem(
		keyName = "advanceToNextBankAfterBlockComplete",
		name = "Advance after block complete",
		description = "Move to the next bank block when manually completing the current one",
		position = 1,
		section = progressSection
	)
	default boolean advanceToNextBankAfterBlockComplete()
	{
		return true;
	}

	@ConfigItem(
		keyName = "startAtBankId",
		name = "Start at bank",
		description = "Bank id to jump to, for example 75 or 39A",
		position = 2,
		section = progressSection
	)
	default String startAtBankId()
	{
		return "";
	}

	@ConfigItem(
		keyName = "applyStartAtBankNow",
		name = "Apply start bank now",
		description = "Immediately complete all earlier banks and jump to the selected bank, then reset this toggle",
		position = 3,
		section = progressSection
	)
	default boolean applyStartAtBankNow()
	{
		return false;
	}

	@ConfigItem(
		keyName = "resetProgressNow",
		name = "Reset progress now",
		description = "Reset all saved guide progress for the current RuneLite profile, then reset this toggle",
		position = 4,
		section = progressSection
	)
	default boolean resetProgressNow()
	{
		return false;
	}

	@ConfigItem(
		keyName = "nextStepKeybind",
		name = "Next step hotkey",
		description = "Hotkey to move to the next guide step",
		position = 0,
		section = inputSection
	)
	default Keybind nextStepKeybind()
	{
		return new ModifierlessKeybind(KeyEvent.VK_CLOSE_BRACKET, 0);
	}

	@ConfigItem(
		keyName = "previousStepKeybind",
		name = "Previous step hotkey",
		description = "Hotkey to move to the previous guide step",
		position = 1,
		section = inputSection
	)
	default Keybind previousStepKeybind()
	{
		return new ModifierlessKeybind(KeyEvent.VK_OPEN_BRACKET, 0);
	}

	@ConfigItem(
		keyName = "nextStepMouseBind",
		name = "Next step mouse bind",
		description = "Mouse button to move to the next guide step",
		position = 2,
		section = inputSection
	)
	default BoatyMouseBind nextStepMouseBind()
	{
		return BoatyMouseBind.NONE;
	}

	@ConfigItem(
		keyName = "previousStepMouseBind",
		name = "Previous step mouse bind",
		description = "Mouse button to move to the previous guide step",
		position = 3,
		section = inputSection
	)
	default BoatyMouseBind previousStepMouseBind()
	{
		return BoatyMouseBind.NONE;
	}
}
