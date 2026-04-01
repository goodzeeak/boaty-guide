package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideStep
{
	private String globalId;
	private int globalIndex;
	private int episodeId;
	private String bankId;
	private int stepIndex;
	private String text;
	private String rawText;
	private StepType stepType = StepType.MANUAL_NOTE;
	private List<GuideQuestRef> questRefs = Collections.emptyList();
	private List<GuideNpc> npcRefs = Collections.emptyList();
	private List<GuideLocation> locationRefs = Collections.emptyList();
	private List<GuideItem> itemRefs = Collections.emptyList();
	private List<GuideTransportRef> transportRefs = Collections.emptyList();
	private List<GuideDialogueRef> dialogueRefs = Collections.emptyList();
	private List<GuideActionRef> actionRefs = Collections.emptyList();
	private List<String> substeps = Collections.emptyList();
	private List<String> adviceLines = Collections.emptyList();
	private List<String> unresolvedMentions = Collections.emptyList();
	private List<String> notes = Collections.emptyList();
	private List<String> tags = Collections.emptyList();

	public String getGlobalId()
	{
		return globalId;
	}

	public int getGlobalIndex()
	{
		return globalIndex;
	}

	public int getEpisodeId()
	{
		return episodeId;
	}

	public String getBankId()
	{
		return bankId;
	}

	public int getStepIndex()
	{
		return stepIndex;
	}

	public String getText()
	{
		return text;
	}

	public String getRawText()
	{
		return rawText;
	}

	public StepType getStepType()
	{
		return stepType;
	}

	public List<GuideQuestRef> getQuestRefs()
	{
		return questRefs;
	}

	public List<GuideNpc> getNpcRefs()
	{
		return npcRefs;
	}

	public List<GuideLocation> getLocationRefs()
	{
		return locationRefs;
	}

	public List<GuideItem> getItemRefs()
	{
		return itemRefs;
	}

	public List<GuideTransportRef> getTransportRefs()
	{
		return transportRefs;
	}

	public List<GuideDialogueRef> getDialogueRefs()
	{
		return dialogueRefs;
	}

	public List<GuideActionRef> getActionRefs()
	{
		return actionRefs;
	}

	public List<String> getSubsteps()
	{
		return substeps;
	}

	public List<String> getAdviceLines()
	{
		return adviceLines;
	}

	public List<String> getUnresolvedMentions()
	{
		return unresolvedMentions;
	}

	public List<String> getNotes()
	{
		return notes;
	}

	public List<String> getTags()
	{
		return tags;
	}

	public String summaryLine()
	{
		return globalIndex + 1 + ". " + text;
	}
}
