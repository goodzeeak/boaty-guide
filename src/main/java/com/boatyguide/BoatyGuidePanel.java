package com.boatyguide;

import com.boatyguide.guide.GuideStep;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.GridLayout;
import java.util.ArrayList;
import java.util.List;
import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.border.EmptyBorder;
import net.runelite.client.ui.ColorScheme;
import net.runelite.client.ui.FontManager;
import net.runelite.client.ui.PluginPanel;

class BoatyGuidePanel extends PluginPanel
{
	private static final Color CURRENT_LABEL = new Color(255, 191, 92);
	private static final Color NEXT_LABEL = new Color(140, 189, 255);
	private static final Color BODY_TEXT = new Color(225, 225, 225);
	private static final Color SECONDARY_TEXT = new Color(214, 214, 214);
	private static final Color ADVICE_LABEL = new Color(214, 143, 255);

	private final JTextArea currentStepText = createTextArea(FontManager.getRunescapeFont(), Color.WHITE);
	private final JTextArea substepsText = createTextArea(FontManager.getRunescapeSmallFont(), BODY_TEXT);
	private final JTextArea adviceText = createTextArea(FontManager.getRunescapeSmallFont(), BODY_TEXT);
	private final JTextArea withdrawText = createTextArea(FontManager.getRunescapeSmallFont(), BODY_TEXT);
	private final JPanel nextStepsContainer = new JPanel();
	private final JComponent substepsSection;
	private final JComponent adviceSection;

	private final JButton previousButton = new JButton("Previous");
	private final JButton nextButton = new JButton("Next");
	private final JButton completeBlockButton = new JButton("Complete Block");

	BoatyGuidePanel()
	{
		super(false);
		setLayout(new BorderLayout());
		setBackground(ColorScheme.DARK_GRAY_COLOR);
		setBorder(new EmptyBorder(6, 6, 6, 6));

		nextStepsContainer.setLayout(new BoxLayout(nextStepsContainer, BoxLayout.Y_AXIS));
		nextStepsContainer.setBackground(ColorScheme.DARKER_GRAY_COLOR);
		nextStepsContainer.setAlignmentX(Component.LEFT_ALIGNMENT);

		JPanel content = new JPanel();
		content.setLayout(new BoxLayout(content, BoxLayout.Y_AXIS));
		content.setBackground(ColorScheme.DARK_GRAY_COLOR);
		content.add(buildTextSection("Current Step", currentStepText, CURRENT_LABEL));
		substepsSection = buildTextSection("Required For This Step", substepsText, NEXT_LABEL);
		substepsSection.setVisible(false);
		content.add(Box.createVerticalStrut(8));
		content.add(substepsSection);
		adviceSection = buildTextSection("Advice", adviceText, ADVICE_LABEL);
		adviceSection.setVisible(false);
		content.add(Box.createVerticalStrut(8));
		content.add(adviceSection);
		content.add(Box.createVerticalStrut(8));
		content.add(buildTextSection("Withdraw", withdrawText, CURRENT_LABEL));
		content.add(Box.createVerticalStrut(8));
		content.add(buildStackSection("Next Steps In This Block", nextStepsContainer, NEXT_LABEL));

		JScrollPane scrollPane = new JScrollPane(content);
		scrollPane.setBorder(BorderFactory.createEmptyBorder());
		scrollPane.getViewport().setBackground(ColorScheme.DARK_GRAY_COLOR);
		scrollPane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

		add(scrollPane, BorderLayout.CENTER);
		add(buildActions(), BorderLayout.SOUTH);
	}

	JButton getPreviousButton()
	{
		return previousButton;
	}

	JButton getNextButton()
	{
		return nextButton;
	}

	JButton getCompleteBlockButton()
	{
		return completeBlockButton;
	}

	void render(
		GuideStep step,
		List<String> adviceLines,
		List<String> withdrawLines,
		List<GuideStep> upcomingSteps)
	{
		currentStepText.setText(step.getText());
		substepsText.setText(joinSubsteps(step.getSubsteps()));
		substepsSection.setVisible(!step.getSubsteps().isEmpty());
		adviceText.setText(joinAdviceLines(adviceLines));
		adviceSection.setVisible(!adviceLines.isEmpty());
		withdrawText.setText(joinWithdrawLines(withdrawLines));
		populateNextSteps(upcomingSteps);
	}

	void setProgressActionState(boolean showCompleteBlockButton, boolean currentBankCompleted)
	{
		completeBlockButton.setVisible(showCompleteBlockButton);
		completeBlockButton.setText(currentBankCompleted ? "Uncomplete Block" : "Complete Block");
	}

	private JComponent buildTextSection(String title, JTextArea area, Color labelColor)
	{
		JPanel panel = createSectionPanel();
		panel.setLayout(new BorderLayout(0, 8));
		panel.add(makeSectionLabel(title, labelColor), BorderLayout.NORTH);
		panel.add(area, BorderLayout.CENTER);
		return panel;
	}

	private JComponent buildStackSection(String title, JPanel body, Color labelColor)
	{
		JPanel panel = createSectionPanel();
		panel.setLayout(new BorderLayout(0, 8));
		panel.add(makeSectionLabel(title, labelColor), BorderLayout.NORTH);
		panel.add(body, BorderLayout.CENTER);
		return panel;
	}

	private JComponent buildActions()
	{
		JPanel panel = new JPanel(new GridLayout(0, 2, 6, 6));
		panel.setBackground(ColorScheme.DARK_GRAY_COLOR);
		panel.setBorder(new EmptyBorder(8, 0, 0, 0));
		styleButton(previousButton);
		styleButton(nextButton);
		styleButton(completeBlockButton);
		panel.add(previousButton);
		panel.add(nextButton);
		panel.add(completeBlockButton);
		return panel;
	}

	private JPanel createSectionPanel()
	{
		JPanel panel = new JPanel();
		panel.setBackground(ColorScheme.DARKER_GRAY_COLOR);
		panel.setBorder(BorderFactory.createCompoundBorder(
			BorderFactory.createMatteBorder(1, 0, 0, 0, ColorScheme.DARK_GRAY_COLOR),
			new EmptyBorder(10, 10, 10, 10)
		));
		panel.setAlignmentX(Component.LEFT_ALIGNMENT);
		return panel;
	}

	private void populateNextSteps(List<GuideStep> upcomingSteps)
	{
		nextStepsContainer.removeAll();

		if (upcomingSteps.isEmpty())
		{
			nextStepsContainer.add(createStepBlock("This is the last step before the next bank block.", List.of(), false));
			return;
		}

		for (int i = 0; i < upcomingSteps.size(); i++)
		{
			nextStepsContainer.add(createStepBlock(upcomingSteps.get(i).getText(), upcomingSteps.get(i).getSubsteps(), i == 0));
			if (i < upcomingSteps.size() - 1)
			{
				nextStepsContainer.add(Box.createVerticalStrut(10));
			}
		}
	}

	private JComponent createStepBlock(String text, List<String> substeps, boolean nextImmediate)
	{
		JTextArea area = createTextArea(
			nextImmediate ? FontManager.getRunescapeFont() : FontManager.getRunescapeSmallFont(),
			nextImmediate ? new Color(236, 236, 236) : SECONDARY_TEXT
		);
		StringBuilder builder = new StringBuilder(text);
		if (!substeps.isEmpty())
		{
			for (String substep : substeps)
			{
				builder.append("\n• ").append(substep);
			}
		}
		area.setText(builder.toString());

		JPanel panel = new JPanel(new BorderLayout());
		panel.setOpaque(true);
		panel.setBackground(nextImmediate ? new Color(54, 59, 68) : ColorScheme.DARKER_GRAY_COLOR);
		panel.setBorder(new EmptyBorder(7, 8, 7, 8));
		panel.setAlignmentX(Component.LEFT_ALIGNMENT);
		panel.add(area, BorderLayout.CENTER);
		return panel;
	}

	private static String joinAdviceLines(List<String> adviceLines)
	{
		if (adviceLines.isEmpty())
		{
			return "";
		}

		return String.join("\n\n", adviceLines);
	}

	private static String joinWithdrawLines(List<String> withdrawLines)
	{
		if (withdrawLines.isEmpty())
		{
			return "Nothing to withdraw for this block.";
		}

		return String.join("\n\n", withdrawLines);
	}

	private static String joinSubsteps(List<String> substeps)
	{
		if (substeps.isEmpty())
		{
			return "";
		}

		List<String> lines = new ArrayList<>();
		for (String substep : substeps)
		{
			lines.add("• " + substep);
		}
		return String.join("\n", lines);
	}

	private static JTextArea createTextArea(java.awt.Font font, Color color)
	{
		JTextArea area = new JTextArea();
		area.setLineWrap(true);
		area.setWrapStyleWord(true);
		area.setEditable(false);
		area.setFocusable(false);
		area.setOpaque(false);
		area.setForeground(color);
		area.setFont(font);
		area.setBorder(BorderFactory.createEmptyBorder());
		return area;
	}

	private static JComponent makeSectionLabel(String text, Color color)
	{
		JTextArea label = new JTextArea(text);
		label.setLineWrap(true);
		label.setWrapStyleWord(true);
		label.setEditable(false);
		label.setFocusable(false);
		label.setOpaque(false);
		label.setForeground(color);
		label.setFont(FontManager.getRunescapeBoldFont());
		label.setBorder(BorderFactory.createEmptyBorder());
		return label;
	}

	private static void styleButton(JButton button)
	{
		button.setFocusPainted(false);
		button.setBackground(ColorScheme.DARKER_GRAY_COLOR);
		button.setForeground(Color.WHITE);
		button.setBorder(BorderFactory.createLineBorder(ColorScheme.DARK_GRAY_COLOR.brighter()));
	}
}
