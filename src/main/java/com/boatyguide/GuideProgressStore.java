package com.boatyguide;

import java.util.Set;

public interface GuideProgressStore
{
	GuideProgressSnapshot load(String guideVersion);

	void save(String guideVersion, GuideProgressSnapshot snapshot);

	void reset(String guideVersion);

	final class GuideProgressSnapshot
	{
		private final String currentStepId;
		private final Set<String> completedStepIds;

		public GuideProgressSnapshot(String currentStepId, Set<String> completedStepIds)
		{
			this.currentStepId = currentStepId;
			this.completedStepIds = completedStepIds;
		}

		public String getCurrentStepId()
		{
			return currentStepId;
		}

		public Set<String> getCompletedStepIds()
		{
			return completedStepIds;
		}
	}
}
