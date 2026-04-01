package com.boatyguide;

import com.boatyguide.guide.GuideData;
import com.boatyguide.guide.GuideDataLoader;
import org.junit.Assert;
import org.junit.Test;

public class GuideDataLoaderTest
{
	@Test
	public void loadsGeneratedGuideData() throws Exception
	{
		GuideDataLoader loader = new GuideDataLoader();
		GuideData data = loader.load();

		Assert.assertNotNull(data);
		Assert.assertEquals("3.0", data.getVersion());
		Assert.assertTrue(data.getTotalSteps() > 1000);
		Assert.assertFalse(data.getEpisodes().isEmpty());
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.anyMatch(bank -> bank.getWithdrawStepText() != null && !bank.getWithdrawStepText().isBlank()));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.anyMatch(bank -> bank.getExitStepText() != null && !bank.getExitStepText().isBlank()));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> !step.getSubsteps().isEmpty()));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> !step.getAdviceLines().isEmpty()));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getText().equals("Complete Tourist Trap")
				&& step.getAdviceLines().stream().anyMatch(line -> line.contains("Mercenary Captain"))));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getRawText().startsWith("Kill a Chicken.")
				&& step.getAdviceLines().stream().anyMatch(line -> line.contains("feather"))
				&& !step.getText().contains("Make sure you get a feather")));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getGlobalId().equals("e11_b199_s1")
				&& step.getText().contains("Talk to Demon Butler")
				&& step.getAdviceLines().isEmpty()));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getGlobalId().equals("e2_b36_s12")
				&& !step.getText().contains("Withdraw Air staff")
				&& step.getAdviceLines().stream().anyMatch(line -> line.startsWith("Withdraw Air staff"))));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getGlobalId().equals("e2_b33_s2")
				&& step.getText().equals("Complete Murder Mystery")
				&& step.getSubsteps().stream().anyMatch(line -> line.contains("Barcrawl"))));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getGlobalId().equals("e2_b28_s8")
				&& step.getSubsteps().stream().anyMatch(line -> line.contains("Balls of Wool"))));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getGlobalId().equals("e3_b105_s7")
				&& step.getText().equals("Find your tunnel")
				&& step.getAdviceLines().stream().anyMatch(line -> line.startsWith("Enter a Melee brother Mound"))));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getGlobalId().equals("e1_b11_s7")
				&& step.getText().equals("Use the Edgeville and Ardougne wilderness lever 4 times.")
				&& step.getAdviceLines().stream().anyMatch(line -> line.contains("Wilderness and Ardougne Diary"))));
		Assert.assertTrue(data.getEpisodes().stream()
			.flatMap(episode -> episode.getBanks().stream())
			.flatMap(bank -> bank.getSteps().stream())
			.anyMatch(step -> step.getGlobalId().equals("e3_b99_s12")
				&& step.getText().equals("Get 10 signatures for Ghost's Ahoy.")
				&& step.getAdviceLines().stream().anyMatch(line -> line.contains("Ectotokens"))));
		Assert.assertTrue(data.findStep(data.getOrderedSteps().get(0).getGlobalId()).isPresent());
	}
}
