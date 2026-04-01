package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideBank
{
	private String bankId;
	private String title;
	private String withdrawStepText;
	private String exitStepText;
	private List<String> transitionNotes = Collections.emptyList();
	private List<String> adviceLines = Collections.emptyList();
	private List<GuideStep> steps = Collections.emptyList();
	private List<GuideItem> withdrawItems = Collections.emptyList();

	public String getBankId()
	{
		return bankId;
	}

	public String getTitle()
	{
		return title;
	}

	public String getWithdrawStepText()
	{
		return withdrawStepText;
	}

	public String getExitStepText()
	{
		return exitStepText;
	}

	public List<String> getTransitionNotes()
	{
		return transitionNotes;
	}

	public List<String> getAdviceLines()
	{
		return adviceLines;
	}

	public List<GuideStep> getSteps()
	{
		return steps;
	}

	public List<GuideItem> getWithdrawItems()
	{
		return withdrawItems;
	}
}
