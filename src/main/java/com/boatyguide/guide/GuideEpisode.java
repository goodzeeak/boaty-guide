package com.boatyguide.guide;

import java.util.Collections;
import java.util.List;

public class GuideEpisode
{
	private int episodeId;
	private String title;
	private List<GuideBank> banks = Collections.emptyList();

	public int getEpisodeId()
	{
		return episodeId;
	}

	public String getTitle()
	{
		return title;
	}

	public List<GuideBank> getBanks()
	{
		return banks;
	}
}
