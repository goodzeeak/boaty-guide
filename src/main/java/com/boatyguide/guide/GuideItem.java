package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideItem
{
	private String displayName;
	private String canonicalName;
	private List<Integer> itemIds = Collections.emptyList();
	private int quantity;
	private boolean optional;

	public String getDisplayName()
	{
		return displayName;
	}

	public String getCanonicalName()
	{
		return canonicalName;
	}

	public List<Integer> getItemIds()
	{
		return itemIds;
	}

	public int getQuantity()
	{
		return quantity;
	}

	public boolean isOptional()
	{
		return optional;
	}
}
