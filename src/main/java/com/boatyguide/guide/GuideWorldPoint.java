package com.boatyguide.guide;

import net.runelite.api.coords.WorldPoint;

public class GuideWorldPoint
{
	private int x;
	private int y;
	private int z;

	public int getX()
	{
		return x;
	}

	public int getY()
	{
		return y;
	}

	public int getZ()
	{
		return z;
	}

	public WorldPoint toWorldPoint()
	{
		return new WorldPoint(x, y, z);
	}
}
