package com.boatyguide;

import com.boatyguide.guide.GuideStep;
import java.awt.Color;
import javax.inject.Inject;
import javax.inject.Singleton;

@Singleton
public class CurrentStepOverlay extends BaseBoatyStepOverlay
{
	private static final Color LABEL_CURRENT = new Color(255, 191, 92);

	@Inject
	public CurrentStepOverlay(GuideStateManager guideStateManager, BoatyGuideConfig config)
	{
		super(guideStateManager, config);
	}

	@Override
	protected GuideStep getStep()
	{
		return guideStateManager.getCurrentStep();
	}

	@Override
	protected String getLabel()
	{
		return "Current";
	}

	@Override
	protected Color getLabelColor()
	{
		return LABEL_CURRENT;
	}
}
