package com.boatyguide.guide;

public class GuideTransportRef
{
	private String type;
	private String displayName;
	private GuideLocation origin;
	private GuideLocation destination;
	private Integer objectId;
	private GuideNpc npcRef;
	private GuideLocation locationRef;

	public String getType()
	{
		return type;
	}

	public String getDisplayName()
	{
		return displayName;
	}

	public GuideLocation getOrigin()
	{
		return origin;
	}

	public GuideLocation getDestination()
	{
		return destination;
	}

	public Integer getObjectId()
	{
		return objectId;
	}

	public GuideNpc getNpcRef()
	{
		return npcRef;
	}

	public GuideLocation getLocationRef()
	{
		return locationRef;
	}
}
