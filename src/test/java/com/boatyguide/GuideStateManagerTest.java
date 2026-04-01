package com.boatyguide;

import com.boatyguide.guide.GuideData;
import com.boatyguide.guide.GuideDataLoader;
import com.boatyguide.guide.GuideStep;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import org.junit.Assert;
import org.junit.Test;

public class GuideStateManagerTest
{
	@Test
	public void preservesProgressAcrossReload() throws Exception
	{
		GuideData data = new GuideDataLoader().load();
		InMemoryProgressStore store = new InMemoryProgressStore();
		GuideStateManager manager = new GuideStateManager(store);

		manager.load(data);
		String firstStep = manager.getCurrentStep().getGlobalId();
		manager.next();
		String secondStep = manager.getCurrentStep().getGlobalId();

		GuideStateManager reloaded = new GuideStateManager(store);
		reloaded.load(data);

		Assert.assertNotEquals(firstStep, secondStep);
		Assert.assertEquals(secondStep, reloaded.getCurrentStep().getGlobalId());
		Assert.assertTrue(reloaded.getCompletedStepIds().contains(firstStep));
	}

	@Test
	public void togglesCurrentBankCompletionAndAdvances() throws Exception
	{
		GuideData data = new GuideDataLoader().load();
		InMemoryProgressStore store = new InMemoryProgressStore();
		GuideStateManager manager = new GuideStateManager(store);

		manager.load(data);
		List<GuideStep> firstBankSteps = manager.getCurrentBank().orElseThrow().getSteps();
		String nextBankId = manager.getNextBank().orElseThrow().getBankId();

		manager.toggleCurrentBankCompleted(true);

		Assert.assertTrue(firstBankSteps.stream().allMatch(manager::isCompleted));
		Assert.assertEquals(nextBankId, manager.getCurrentStep().getBankId());

		manager.jumpToBank(firstBankSteps.get(0).getBankId());
		manager.toggleCurrentBankCompleted(false);

		Assert.assertTrue(firstBankSteps.stream().noneMatch(manager::isCompleted));
	}

	@Test
	public void setsProgressToConfiguredBank() throws Exception
	{
		GuideData data = new GuideDataLoader().load();
		InMemoryProgressStore store = new InMemoryProgressStore();
		GuideStateManager manager = new GuideStateManager(store);

		manager.load(data);

		Assert.assertTrue(manager.setProgressToBank("75"));
		Assert.assertEquals("75", manager.getCurrentStep().getBankId());
		Assert.assertTrue(data.getOrderedBanks().stream()
			.takeWhile(bank -> !bank.getBankId().equals("75"))
			.flatMap(bank -> bank.getSteps().stream())
			.allMatch(manager::isCompleted));
	}

	@Test
	public void nextCompletesAndPreviousUncompletes() throws Exception
	{
		GuideData data = new GuideDataLoader().load();
		InMemoryProgressStore store = new InMemoryProgressStore();
		GuideStateManager manager = new GuideStateManager(store);

		manager.load(data);
		String firstStepId = manager.getCurrentStep().getGlobalId();
		String secondStepId = data.getOrderedSteps().get(1).getGlobalId();

		manager.next();

		Assert.assertTrue(manager.getCompletedStepIds().contains(firstStepId));
		Assert.assertEquals(secondStepId, manager.getCurrentStep().getGlobalId());

		manager.previous();

		Assert.assertEquals(firstStepId, manager.getCurrentStep().getGlobalId());
		Assert.assertFalse(manager.getCompletedStepIds().contains(firstStepId));
	}

	@Test
	public void skipsWithdrawStepsInNavigation() throws Exception
	{
		GuideData data = new GuideDataLoader().load();
		InMemoryProgressStore store = new InMemoryProgressStore();
		GuideStateManager manager = new GuideStateManager(store);

		manager.load(data);
		manager.jumpToStep("e1_b0_s9");

		manager.next();

		Assert.assertEquals("e1_b1_s1", manager.getCurrentStep().getGlobalId());
		Assert.assertNotEquals("WITHDRAW", manager.getCurrentStep().getStepType().name());
	}

	@Test
	public void resolvesWithdrawDetailsSeparatelyFromAdvice() throws Exception
	{
		GuideData data = new GuideDataLoader().load();
		InMemoryProgressStore store = new InMemoryProgressStore();
		GuideStateManager manager = new GuideStateManager(store);

		manager.load(data);
		manager.jumpToStep("e2_b36_s12");

		List<String> withdrawLines = manager.getCurrentWithdrawLines();
		List<String> adviceLines = manager.getCurrentAdviceLines();

		Assert.assertTrue(withdrawLines.stream().anyMatch(line -> line.startsWith("Withdraw: Coins, Pestle & Mortar")));
		Assert.assertTrue(withdrawLines.stream().anyMatch(line -> line.startsWith("Withdraw Air staff")));
		Assert.assertFalse(adviceLines.stream().anyMatch(line -> line.startsWith("Withdraw Air staff")));
	}

	@Test
	public void allowsHandoffWhenOnlyTrailingBankAdviceRemains() throws Exception
	{
		GuideData data = new GuideDataLoader().load();
		InMemoryProgressStore store = new InMemoryProgressStore();
		GuideStateManager manager = new GuideStateManager(store);

		manager.load(data);
		manager.jumpToStep("e1_b0_s9");

		Assert.assertTrue(manager.isDepositHandoffStep());
		Assert.assertTrue(manager.getCurrentWithdrawLines().stream()
			.anyMatch(line -> line.startsWith("Withdraw: Coins, Air Runes, Mind Runes")));
	}

	private static class InMemoryProgressStore implements GuideProgressStore
	{
		private String currentStep;
		private Set<String> completed = new LinkedHashSet<>();

		@Override
		public GuideProgressSnapshot load(String guideVersion)
		{
			return new GuideProgressSnapshot(currentStep, new LinkedHashSet<>(completed));
		}

		@Override
		public void save(String guideVersion, GuideProgressSnapshot snapshot)
		{
			currentStep = snapshot.getCurrentStepId();
			completed = new LinkedHashSet<>(snapshot.getCompletedStepIds());
		}

		@Override
		public void reset(String guideVersion)
		{
			currentStep = null;
			completed.clear();
		}
	}
}
