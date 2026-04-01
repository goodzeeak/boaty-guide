package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideNpc
{
	private String displayName;
	private String canonicalName;
	private List<Integer> npcIds = Collections.emptyList();
	private List<String> locationHints = Collections.emptyList();

	public String getDisplayName()
	{
		return displayName;
	}

	public String getCanonicalName()
	{
		return canonicalName;
	}

	public List<Integer> getNpcIds()
	{
		return npcIds;
	}

	public List<String> getLocationHints()
	{
		return locationHints;
	}
}
