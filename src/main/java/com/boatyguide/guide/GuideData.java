package com.boatyguide.guide;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class GuideData
{
	private String version;
	private String source;
	private int totalSteps;
	private Map<String, Object> diagnostics = Collections.emptyMap();
	private List<GuideEpisode> episodes = Collections.emptyList();

	private transient Map<String, GuideStep> stepsById = Collections.emptyMap();
	private transient List<GuideStep> steps = Collections.emptyList();
	private transient Map<String, List<GuideStep>> stepsByBank = Collections.emptyMap();
	private transient Map<String, List<GuideStep>> stepsByQuest = Collections.emptyMap();
	private transient List<GuideBank> banks = Collections.emptyList();
	private transient Map<String, Integer> bankIndexes = Collections.emptyMap();

	public String getVersion()
	{
		return version;
	}

	public String getSource()
	{
		return source;
	}

	public int getTotalSteps()
	{
		return totalSteps;
	}

	public Map<String, Object> getDiagnostics()
	{
		return diagnostics;
	}

	public List<GuideEpisode> getEpisodes()
	{
		return episodes;
	}

	public void buildIndexes()
	{
		Map<String, GuideStep> byId = new LinkedHashMap<>();
		List<GuideStep> ordered = new ArrayList<>();
		Map<String, List<GuideStep>> byBank = new LinkedHashMap<>();
		Map<String, List<GuideStep>> byQuest = new LinkedHashMap<>();
		List<GuideBank> orderedBanks = new ArrayList<>();
		Map<String, Integer> byBankIndex = new LinkedHashMap<>();

		for (GuideEpisode episode : episodes)
		{
			for (GuideBank bank : episode.getBanks())
			{
				byBankIndex.put(bank.getBankId(), orderedBanks.size());
				orderedBanks.add(bank);
				for (GuideStep step : bank.getSteps())
				{
					ordered.add(step);
					byId.put(step.getGlobalId(), step);
					byBank.computeIfAbsent(step.getBankId(), ignored -> new ArrayList<>()).add(step);
					for (GuideQuestRef questRef : step.getQuestRefs())
					{
						byQuest.computeIfAbsent(questRef.getCanonicalName(), ignored -> new ArrayList<>()).add(step);
					}
				}
			}
		}

		this.stepsById = byId;
		this.steps = Collections.unmodifiableList(ordered);
		this.stepsByBank = freezeMap(byBank);
		this.stepsByQuest = freezeMap(byQuest);
		this.banks = Collections.unmodifiableList(orderedBanks);
		this.bankIndexes = Collections.unmodifiableMap(byBankIndex);
	}

	private static Map<String, List<GuideStep>> freezeMap(Map<String, List<GuideStep>> input)
	{
		Map<String, List<GuideStep>> output = new LinkedHashMap<>();
		input.forEach((key, value) -> output.put(key, Collections.unmodifiableList(value)));
		return Collections.unmodifiableMap(output);
	}

	public int getBankCount()
	{
		return episodes.stream().mapToInt(ep -> ep.getBanks().size()).sum();
	}

	public Optional<String> getFirstStepText()
	{
		return steps.stream().map(GuideStep::getText).findFirst();
	}

	public Optional<GuideStep> findStep(String globalId)
	{
		return Optional.ofNullable(stepsById.get(globalId));
	}

	public List<GuideStep> getOrderedSteps()
	{
		return steps;
	}

	public List<GuideStep> getStepsForBank(String bankId)
	{
		return stepsByBank.getOrDefault(bankId, Collections.emptyList());
	}

	public List<GuideStep> getStepsForQuest(String canonicalQuest)
	{
		return stepsByQuest.getOrDefault(canonicalQuest, Collections.emptyList());
	}

	public List<GuideBank> getOrderedBanks()
	{
		return banks;
	}

	public Optional<GuideBank> getNextBank(String bankId)
	{
		Integer index = bankIndexes.get(bankId);
		if (index == null || index + 1 >= banks.size())
		{
			return Optional.empty();
		}
		return Optional.ofNullable(banks.get(index + 1));
	}

	public Optional<GuideStep> findNextUnresolvedStep(int fromIndex)
	{
		return steps.stream()
			.filter(step -> step.getGlobalIndex() >= fromIndex)
			.filter(step -> !step.getUnresolvedMentions().isEmpty())
			.findFirst();
	}
}
