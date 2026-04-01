package com.boatyguide;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.util.ArrayList;
import java.util.List;
import javax.inject.Inject;
import javax.inject.Singleton;
import net.runelite.client.ui.overlay.OverlayLayer;
import net.runelite.client.ui.overlay.OverlayPanel;
import net.runelite.client.ui.overlay.OverlayPosition;
import net.runelite.client.ui.overlay.OverlayPriority;
import net.runelite.client.ui.overlay.components.LineComponent;

@Singleton
@SuppressWarnings("deprecation")
public class AdviceOverlay extends OverlayPanel
{
	private static final Color LABEL = new Color(214, 143, 255);
	private static final Color VALUE = new Color(240, 240, 240);

	private final GuideStateManager guideStateManager;
	private final BoatyGuideConfig config;

	@Inject
	public AdviceOverlay(GuideStateManager guideStateManager, BoatyGuideConfig config)
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
		if (!config.showOverlay() || !config.showAdviceOverlay())
		{
			return null;
		}

		String advice = guideStateManager.getCurrentAdvicePreview().orElse(null);
		if (advice == null || advice.isBlank())
		{
			return null;
		}

		panelComponent.setBackgroundColor(new Color(36, 31, 43, 190));
		panelComponent.setPreferredSize(new Dimension(260, 0));
		addWrappedLine("Advice", advice);
		return super.render(graphics);
	}

	private void addWrappedLine(String label, String text)
	{
		List<String> chunks = wrapText(text, 34);
		for (int i = 0; i < chunks.size(); i++)
		{
			panelComponent.getChildren().add(LineComponent.builder()
				.left(i == 0 ? label : "")
				.right(chunks.get(i))
				.leftColor(LABEL)
				.rightColor(VALUE)
				.build());
		}
	}

	private static List<String> wrapText(String text, int maxWidth)
	{
		List<String> lines = new ArrayList<>();
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
