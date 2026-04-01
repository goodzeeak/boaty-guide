package com.boatyguide;

import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.stream.Collectors;
import javax.inject.Inject;
import javax.inject.Singleton;
import net.runelite.client.config.ConfigManager;

@Singleton
public class ConfigGuideProgressStore implements GuideProgressStore
{
	private static final String GROUP = "boatyguide.progress";
	private static final String CURRENT_KEY = "currentStep";
	private static final String COMPLETED_KEY = "completedSteps";

	private final ConfigManager configManager;

	@Inject
	public ConfigGuideProgressStore(ConfigManager configManager)
	{
		this.configManager = configManager;
	}

	@Override
	public GuideProgressSnapshot load(String guideVersion)
	{
		String current = configManager.getRSProfileConfiguration(GROUP, key(guideVersion, CURRENT_KEY));
		String completed = configManager.getRSProfileConfiguration(GROUP, key(guideVersion, COMPLETED_KEY));
		Set<String> completedIds = completed == null || completed.isBlank()
			? new LinkedHashSet<>()
			: Arrays.stream(completed.split(","))
				.map(String::trim)
				.filter(value -> !value.isEmpty())
				.collect(Collectors.toCollection(LinkedHashSet::new));
		return new GuideProgressSnapshot(current, completedIds);
	}

	@Override
	public void save(String guideVersion, GuideProgressSnapshot snapshot)
	{
		configManager.setRSProfileConfiguration(GROUP, key(guideVersion, CURRENT_KEY), snapshot.getCurrentStepId());
		String completed = String.join(",", snapshot.getCompletedStepIds());
		configManager.setRSProfileConfiguration(GROUP, key(guideVersion, COMPLETED_KEY), completed);
	}

	@Override
	public void reset(String guideVersion)
	{
		configManager.unsetRSProfileConfiguration(GROUP, key(guideVersion, CURRENT_KEY));
		configManager.unsetRSProfileConfiguration(GROUP, key(guideVersion, COMPLETED_KEY));
	}

	private static String key(String guideVersion, String suffix)
	{
		return guideVersion + "." + suffix;
	}
}
