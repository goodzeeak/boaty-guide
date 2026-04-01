package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideDialogueRef
{
	private GuideNpc npcRef;
	private String promptText;
	private List<Integer> optionSequence = Collections.emptyList();

	public GuideNpc getNpcRef()
	{
		return npcRef;
	}

	public String getPromptText()
	{
		return promptText;
	}

	public List<Integer> getOptionSequence()
	{
		return optionSequence;
	}
}
