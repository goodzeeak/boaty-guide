package com.boatyguide;

import com.boatyguide.guide.GuideStep;
import java.awt.Color;
import javax.inject.Inject;
import javax.inject.Singleton;

@Singleton
public class NextStepOverlay extends BaseBoatyStepOverlay
{
	private static final Color LABEL_NEXT = new Color(140, 189, 255);

	@Inject
	public NextStepOverlay(GuideStateManager guideStateManager, BoatyGuideConfig config)
	{
		super(guideStateManager, config);
	}

	@Override
	protected GuideStep getStep()
	{
		return guideStateManager.getNextOverlayStep().orElse(null);
	}

	@Override
	protected String getLabel()
	{
		return "Next";
	}

	@Override
	protected Color getLabelColor()
	{
		return LABEL_NEXT;
	}
}
