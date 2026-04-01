package com.boatyguide;

import com.boatyguide.guide.GuideBank;
import com.boatyguide.guide.GuideData;
import com.boatyguide.guide.GuideEpisode;
import com.boatyguide.guide.GuideStep;
import com.boatyguide.guide.StepType;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import javax.inject.Inject;
import javax.inject.Singleton;

@Singleton
public class GuideStateManager
{
	private final GuideProgressStore progressStore;
	private GuideData guideData;
	private GuideStep currentStep;
	private final Set<String> completedStepIds = new LinkedHashSet<>();

	@Inject
	public GuideStateManager(GuideProgressStore progressStore)
	{
		this.progressStore = progressStore;
	}

	public void load(GuideData guideData)
	{
		this.guideData = guideData;
		completedStepIds.clear();
		GuideProgressStore.GuideProgressSnapshot snapshot = progressStore.load(guideData.getVersion());
		completedStepIds.addAll(snapshot.getCompletedStepIds());
		currentStep = resolveNavigableStep(guideData.findStep(snapshot.getCurrentStepId()).orElse(null))
			.orElseGet(() -> guideData.getOrderedSteps().stream()
				.filter(this::isNavigableStep)
				.findFirst()
				.orElse(guideData.getOrderedSteps().get(0)));
		persist();
	}

	public GuideStep getCurrentStep()
	{
		return currentStep;
	}

	public int getCurrentIndex()
	{
		return currentStep == null ? 0 : currentStep.getGlobalIndex();
	}

	public void next()
	{
		if (currentStep == null)
		{
			return;
		}

		completedStepIds.add(currentStep.getGlobalId());
		currentStep = findNextNavigableStep(currentStep).orElse(currentStep);
		persist();
	}

	public void previous()
	{
		if (currentStep == null)
		{
			return;
		}

		currentStep = findPreviousNavigableStep(currentStep).orElse(currentStep);
		completedStepIds.remove(currentStep.getGlobalId());
		persist();
	}

	public void jumpToIndex(int index)
	{
		currentStep = resolveNavigableStep(guideData.getOrderedSteps().get(index)).orElse(currentStep);
		persist();
	}

	public void jumpToStep(String globalId)
	{
		currentStep = resolveNavigableStep(guideData.findStep(globalId).orElse(null)).orElse(currentStep);
		persist();
	}

	public void jumpToBank(String bankId)
	{
		Optional<GuideBank> bank = guideData.getOrderedBanks().stream()
			.filter(candidate -> candidate.getBankId().equals(bankId))
			.findFirst();
		if (bank.isPresent())
		{
			currentStep = getFirstNavigableStep(bank.get()).orElse(currentStep);
			persist();
		}
	}

	public boolean setProgressToBank(String bankId)
	{
		if (bankId == null || bankId.isBlank())
		{
			return false;
		}

		String normalizedBankId = bankId.trim().toUpperCase();
		Optional<GuideBank> targetBank = guideData.getOrderedBanks().stream()
			.filter(bank -> bank.getBankId() != null && bank.getBankId().trim().equalsIgnoreCase(normalizedBankId))
			.findFirst();

		if (targetBank.isEmpty() || targetBank.get().getSteps().isEmpty() || getFirstNavigableStep(targetBank.get()).isEmpty())
		{
			return false;
		}

		completedStepIds.clear();
		for (GuideBank bank : guideData.getOrderedBanks())
		{
			if (bank.getBankId().equalsIgnoreCase(normalizedBankId))
			{
				break;
			}
			bank.getSteps().forEach(step -> completedStepIds.add(step.getGlobalId()));
		}

		currentStep = getFirstNavigableStep(targetBank.get()).orElse(currentStep);
		persist();
		return true;
	}

	public void toggleCurrentBankCompleted(boolean moveToNextBank)
	{
		Optional<GuideBank> currentBank = getCurrentBank();
		if (currentBank.isEmpty())
		{
			return;
		}

		List<GuideStep> bankSteps = currentBank.get().getSteps();
		boolean allCompleted = bankSteps.stream()
			.allMatch(step -> completedStepIds.contains(step.getGlobalId()));

		if (allCompleted)
		{
			bankSteps.forEach(step -> completedStepIds.remove(step.getGlobalId()));
			persist();
			return;
		}

		bankSteps.forEach(step -> completedStepIds.add(step.getGlobalId()));
		if (moveToNextBank)
		{
			getNextBank()
				.flatMap(this::getFirstNavigableStep)
				.ifPresent(nextStep -> currentStep = nextStep);
		}
		persist();
	}

	public boolean isCompleted(GuideStep step)
	{
		return completedStepIds.contains(step.getGlobalId());
	}

	public boolean isCurrentBankCompleted()
	{
		return getCurrentBank()
			.map(bank -> bank.getSteps().stream().allMatch(this::isCompleted))
			.orElse(false);
	}

	public void reset()
	{
		completedStepIds.clear();
		currentStep = guideData.getOrderedSteps().stream()
			.filter(this::isNavigableStep)
			.findFirst()
			.orElse(guideData.getOrderedSteps().get(0));
		progressStore.reset(guideData.getVersion());
		persist();
	}

	public List<GuideStep> getRemainingStepsInCurrentBank(int count)
	{
		Optional<GuideBank> bank = getSidebarBank();
		if (bank.isEmpty())
		{
			return List.of();
		}

		List<GuideStep> remaining = new ArrayList<>();
		if (isDepositHandoffStep())
		{
			for (GuideStep step : bank.get().getSteps())
			{
				if (step.getStepType() == StepType.WITHDRAW)
				{
					continue;
				}
				if (remaining.size() >= count)
				{
					break;
				}
				remaining.add(step);
			}
			return remaining;
		}

		boolean foundCurrent = false;
		for (GuideStep step : bank.get().getSteps())
		{
			if (!foundCurrent)
			{
				foundCurrent = step.getGlobalId().equals(currentStep.getGlobalId());
				continue;
			}

			if (remaining.size() >= count)
			{
				break;
			}
			remaining.add(step);
		}
		return remaining;
	}

	public Optional<GuideStep> getNextOverlayStep()
	{
		if (isDepositHandoffStep())
		{
			return getSidebarBank().flatMap(this::getFirstNavigableStep);
		}

		List<GuideStep> upcoming = getRemainingStepsInCurrentBank(1);
		return upcoming.isEmpty() ? Optional.empty() : Optional.of(upcoming.get(0));
	}

	public Optional<GuideStep> getCurrentBankWithdrawStep()
	{
		return getSidebarBank()
			.flatMap(bank -> bank.getSteps().stream()
				.filter(step -> step.getStepType() == StepType.WITHDRAW)
				.findFirst());
	}

	public List<String> getCurrentWithdrawLines()
	{
		if (currentStep == null)
		{
			return List.of();
		}

		LinkedHashSet<String> lines = new LinkedHashSet<>();
		Optional<GuideBank> sidebarBank = getSidebarBank();
		if (sidebarBank.isPresent())
		{
			String withdrawStepText = sidebarBank.get().getWithdrawStepText();
			if (withdrawStepText != null && !withdrawStepText.isBlank())
			{
				lines.add(withdrawStepText);
			}
		}

		getCurrentBankWithdrawStep().ifPresent(step ->
		{
			lines.addAll(step.getSubsteps());
			lines.addAll(step.getAdviceLines());
		});

		lines.addAll(extractInlineWithdrawDetails(currentStep.getAdviceLines()));
		return List.copyOf(lines);
	}

	public List<String> getCurrentAdviceLines()
	{
		if (currentStep == null)
		{
			return List.of();
		}

		LinkedHashSet<String> advice = new LinkedHashSet<>();
		List<String> withdrawLines = getCurrentWithdrawLines();
		for (String line : currentStep.getAdviceLines())
		{
			if (!withdrawLines.contains(line))
			{
				advice.add(line);
			}
		}

		Optional<GuideBank> contextualBank = getSidebarBank();
		if (contextualBank.isPresent() && (currentStep.getStepIndex() <= 1 || isDepositHandoffStep()))
		{
			advice.addAll(contextualBank.get().getTransitionNotes());
			advice.addAll(contextualBank.get().getAdviceLines());
		}

		return List.copyOf(advice);
	}

	public Optional<String> getCurrentAdvicePreview()
	{
		return getCurrentAdviceLines().stream()
			.filter(line -> line != null && !line.isBlank())
			.findFirst();
	}

	public Optional<GuideBank> getCurrentBank()
	{
		return guideData.getEpisodes().stream()
			.flatMap(ep -> ep.getBanks().stream())
			.filter(bank -> bank.getBankId().equals(currentStep.getBankId()))
			.findFirst();
	}

	public Optional<GuideBank> getSidebarBank()
	{
		if (isDepositHandoffStep())
		{
			return getNextBank();
		}
		return getCurrentBank();
	}

	public Optional<GuideBank> getNextBank()
	{
		return getCurrentBank().flatMap(bank -> guideData.getNextBank(bank.getBankId()));
	}

	public boolean isDepositHandoffStep()
	{
		if (currentStep == null || currentStep.getStepType() != StepType.DEPOSIT)
		{
			return false;
		}

		Optional<GuideBank> currentBank = getCurrentBank();
		Optional<GuideBank> nextBank = getNextBank();
		if (currentBank.isEmpty() || currentBank.get().getSteps().isEmpty() || nextBank.isEmpty())
		{
			return false;
		}

		boolean hasWithdrawStep = nextBank.get().getSteps().stream()
			.anyMatch(step -> step.getStepType() == StepType.WITHDRAW);
		if (!hasWithdrawStep)
		{
			return false;
		}

		List<GuideStep> bankSteps = currentBank.get().getSteps();
		int currentIndex = -1;
		for (int i = 0; i < bankSteps.size(); i++)
		{
			if (bankSteps.get(i).getGlobalId().equals(currentStep.getGlobalId()))
			{
				currentIndex = i;
				break;
			}
		}

		if (currentIndex == -1)
		{
			return false;
		}

		for (int i = currentIndex + 1; i < bankSteps.size(); i++)
		{
			if (!isNonBlockingPostBankStep(bankSteps.get(i)))
			{
				return false;
			}
		}

		return true;
	}

	public Optional<GuideEpisode> getCurrentEpisode()
	{
		return guideData.getEpisodes().stream()
			.filter(ep -> ep.getEpisodeId() == currentStep.getEpisodeId())
			.findFirst();
	}

	public Set<String> getCompletedStepIds()
	{
		return completedStepIds;
	}

	private void persist()
	{
		progressStore.save(
			guideData.getVersion(),
			new GuideProgressStore.GuideProgressSnapshot(currentStep.getGlobalId(), new LinkedHashSet<>(completedStepIds))
		);
	}

	private static List<String> extractInlineWithdrawDetails(List<String> adviceLines)
	{
		List<String> lines = new ArrayList<>();
		boolean collecting = false;

		for (String line : adviceLines)
		{
			if (line == null || line.isBlank())
			{
				continue;
			}

			String lower = line.toLowerCase();
			if (lower.startsWith("withdraw "))
			{
				lines.add(line);
				collecting = true;
				continue;
			}

			if (collecting && (line.startsWith("(") || lower.startsWith("place ") || lower.startsWith("equip ") || lower.startsWith("wear ")))
			{
				lines.add(line);
				continue;
			}

			collecting = false;
		}

		return lines;
	}

	private Optional<GuideStep> resolveNavigableStep(GuideStep step)
	{
		if (step == null)
		{
			return Optional.empty();
		}
		if (isNavigableStep(step))
		{
			return Optional.of(step);
		}
		return findNextNavigableStep(step).or(() -> findPreviousNavigableStep(step));
	}

	private Optional<GuideStep> findNextNavigableStep(GuideStep step)
	{
		List<GuideStep> orderedSteps = guideData.getOrderedSteps();
		for (int i = step.getGlobalIndex() + 1; i < orderedSteps.size(); i++)
		{
			GuideStep candidate = orderedSteps.get(i);
			if (isNavigableStep(candidate))
			{
				return Optional.of(candidate);
			}
		}
		return Optional.empty();
	}

	private Optional<GuideStep> findPreviousNavigableStep(GuideStep step)
	{
		List<GuideStep> orderedSteps = guideData.getOrderedSteps();
		for (int i = step.getGlobalIndex() - 1; i >= 0; i--)
		{
			GuideStep candidate = orderedSteps.get(i);
			if (isNavigableStep(candidate))
			{
				return Optional.of(candidate);
			}
		}
		return Optional.empty();
	}

	private Optional<GuideStep> getFirstNavigableStep(GuideBank bank)
	{
		return bank.getSteps().stream()
			.filter(this::isNavigableStep)
			.findFirst();
	}

	private boolean isNavigableStep(GuideStep step)
	{
		return step.getStepType() != StepType.WITHDRAW;
	}

	private static boolean isNonBlockingPostBankStep(GuideStep step)
	{
		String text = step.getText();
		if (text == null)
		{
			return false;
		}

		String lower = text.toLowerCase();
		return lower.startsWith("keep ")
			|| lower.startsWith("move coins into first bank slot")
			|| lower.startsWith("set bank pin")
			|| lower.startsWith("set your bank up ")
			|| lower.startsWith("set your bank up with");
	}
}
