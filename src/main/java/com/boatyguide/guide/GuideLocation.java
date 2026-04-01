package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideLocation
{
	private String displayName;
	private String canonicalName;
	private List<GuideWorldPoint> worldPoints = Collections.emptyList();
	private List<String> areaHints = Collections.emptyList();

	public String getDisplayName()
	{
		return displayName;
	}

	public String getCanonicalName()
	{
		return canonicalName;
	}

	public List<GuideWorldPoint> getWorldPoints()
	{
		return worldPoints;
	}

	public List<String> getAreaHints()
	{
		return areaHints;
	}

	public GuideWorldPoint getPrimaryPoint()
	{
		return worldPoints.isEmpty() ? null : worldPoints.get(0);
	}
}
