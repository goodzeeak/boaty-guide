package com.boatyguide;

import com.boatyguide.guide.GuideStep;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.util.ArrayList;
import java.util.List;
import net.runelite.client.ui.overlay.OverlayLayer;
import net.runelite.client.ui.overlay.OverlayPanel;
import net.runelite.client.ui.overlay.OverlayPosition;
import net.runelite.client.ui.overlay.OverlayPriority;
import net.runelite.client.ui.overlay.components.LineComponent;

@SuppressWarnings("deprecation")
abstract class BaseBoatyStepOverlay extends OverlayPanel
{
	private static final Color VALUE = Color.WHITE;

	protected final GuideStateManager guideStateManager;
	protected final BoatyGuideConfig config;

	protected BaseBoatyStepOverlay(GuideStateManager guideStateManager, BoatyGuideConfig config)
	{
		this.guideStateManager = guideStateManager;
		this.config = config;
		setPosition(OverlayPosition.TOP_LEFT);
		setLayer(OverlayLayer.UNDER_WIDGETS);
		setPriority(OverlayPriority.HIGH);
	}

	@Override
	public Dimension render(Graphics2D graphics)
	{
		panelComponent.getChildren().clear();
		if (!config.showOverlay())
		{
			return null;
		}

		GuideStep step = getStep();
		if (step == null)
		{
			return null;
		}

		panelComponent.setBackgroundColor(new Color(30, 30, 30, 190));
		panelComponent.setPreferredSize(new Dimension(260, 0));

		addWrappedLine(getLabel(), step.getText(), getLabelColor());
		return super.render(graphics);
	}

	protected abstract GuideStep getStep();

	protected abstract String getLabel();

	protected abstract Color getLabelColor();

	private void addWrappedLine(String label, String text, Color labelColor)
	{
		addWrappedLine(label, text, labelColor, VALUE);
	}

	private void addWrappedLine(String label, String text, Color labelColor, Color valueColor)
	{
		List<String> chunks = wrapText(text, 34);
		for (int i = 0; i < chunks.size(); i++)
		{
			panelComponent.getChildren().add(LineComponent.builder()
				.left(i == 0 ? label : "")
				.right(chunks.get(i))
				.leftColor(labelColor)
				.rightColor(valueColor)
				.build());
		}
	}

	private static List<String> wrapText(String text, int maxWidth)
	{
		List<String> lines = new ArrayList<>();
		if (text == null || text.isBlank())
		{
			lines.add("");
			return lines;
		}

		String[] words = text.trim().split("\\s+");
		StringBuilder current = new StringBuilder();
		for (String word : words)
		{
			if (current.length() == 0)
			{
				current.append(word);
				continue;
			}

			if (current.length() + 1 + word.length() <= maxWidth)
			{
				current.append(' ').append(word);
			}
			else
			{
				lines.add(current.toString());
				current = new StringBuilder(word);
			}
		}

		if (current.length() > 0)
		{
			lines.add(current.toString());
		}

		return lines;
	}
}
