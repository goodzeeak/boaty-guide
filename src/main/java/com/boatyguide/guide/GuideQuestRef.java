package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideQuestRef
{
	private String displayName;
	private String canonicalName;
	private List<String> questStateHints = Collections.emptyList();

	public String getDisplayName()
	{
		return displayName;
	}

	public String getCanonicalName()
	{
		return canonicalName;
	}

	public List<String> getQuestStateHints()
	{
		return questStateHints;
	}
}
