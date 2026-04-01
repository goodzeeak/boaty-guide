package com.boatyguide;

import com.boatyguide.guide.GuideBank;
import com.boatyguide.guide.GuideData;
import com.boatyguide.guide.GuideDataLoader;
import com.boatyguide.guide.GuideStep;
import com.google.inject.Provides;
import java.awt.event.MouseEvent;
import java.util.Optional;
import javax.inject.Inject;
import javax.swing.SwingUtilities;
import net.runelite.client.config.ConfigManager;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.events.ConfigChanged;
import net.runelite.client.input.KeyManager;
import net.runelite.client.input.MouseAdapter;
import net.runelite.client.input.MouseManager;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;
import net.runelite.client.ui.ClientToolbar;
import net.runelite.client.ui.NavigationButton;
import net.runelite.client.ui.overlay.OverlayManager;
import net.runelite.client.util.ImageUtil;
import net.runelite.client.util.HotkeyListener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@PluginDescriptor(
	name = "Boaty Guide",
	description = "Follow Boaty's HCIM Guide V3 in a clean bank-by-bank flow",
	enabledByDefault = true,
	tags = {"guide", "ironman", "questing"}
)
public class BoatyGuidePlugin extends Plugin
{
	private static final Logger log = LoggerFactory.getLogger(BoatyGuidePlugin.class);

	@Inject
	private ClientToolbar clientToolbar;

	@Inject
	private ConfigManager configManager;

	@Inject
	private KeyManager keyManager;

	@Inject
	private MouseManager mouseManager;

	@Inject
	private GuideDataLoader guideDataLoader;

	@Inject
	private GuideStateManager guideStateManager;

	@Inject
	private BoatyGuideConfig config;

	@Inject
	private OverlayManager overlayManager;

	@Inject
	private CurrentStepOverlay currentStepOverlay;

	@Inject
	private NextStepOverlay nextStepOverlay;

	@Inject
	private WithdrawOverlay withdrawOverlay;

	@Inject
	private AdviceOverlay adviceOverlay;

	private NavigationButton navigationButton;
	private BoatyGuidePanel panel;
	private GuideData data;
	private final HotkeyListener nextStepHotkey = new HotkeyListener(() -> config.nextStepKeybind())
	{
		@Override
		public void hotkeyPressed()
		{
			handleNextStep();
		}
	};
	private final HotkeyListener previousStepHotkey = new HotkeyListener(() -> config.previousStepKeybind())
	{
		@Override
		public void hotkeyPressed()
		{
			handlePreviousStep();
		}
	};
	private final MouseAdapter guideMouseAdapter = new MouseAdapter()
	{
		@Override
		public MouseEvent mousePressed(MouseEvent mouseEvent)
		{
			if (data == null)
			{
				return mouseEvent;
			}

			if (config.nextStepMouseBind().matches(mouseEvent))
			{
				handleNextStep();
				mouseEvent.consume();
				return mouseEvent;
			}
			if (config.previousStepMouseBind().matches(mouseEvent))
			{
				handlePreviousStep();
				mouseEvent.consume();
				return mouseEvent;
			}
			return mouseEvent;
		}
	};

	@Provides
	BoatyGuideConfig provideConfig(ConfigManager configManager)
	{
		return configManager.getConfig(BoatyGuideConfig.class);
	}

	@Provides
	GuideProgressStore provideProgressStore(ConfigGuideProgressStore store)
	{
		return store;
	}

	@Override
	protected void startUp() throws Exception
	{
		panel = new BoatyGuidePanel();
		wirePanelActions();
		data = guideDataLoader.load();
		guideStateManager.load(data);
		applyStartBankIfConfigured();
		applyResetProgressIfConfigured();
		navigationButton = NavigationButton.builder()
			.tooltip("Boaty Guide")
			.icon(ImageUtil.loadImageResource(getClass(), "/com/boatyguide/icon.png"))
			.priority(5)
			.panel(panel)
			.build();
		SwingUtilities.invokeLater(() -> clientToolbar.addNavigation(navigationButton));
		overlayManager.add(currentStepOverlay);
		overlayManager.add(withdrawOverlay);
		overlayManager.add(nextStepOverlay);
		overlayManager.add(adviceOverlay);
		keyManager.registerKeyListener(previousStepHotkey);
		keyManager.registerKeyListener(nextStepHotkey);
		mouseManager.registerMouseListener(guideMouseAdapter);
		refreshPanel();
		log.info("Loaded guide version {} with {} steps", data.getVersion(), data.getTotalSteps());
	}

	@Override
	protected void shutDown()
	{
		if (navigationButton != null)
		{
			SwingUtilities.invokeLater(() -> clientToolbar.removeNavigation(navigationButton));
			navigationButton = null;
		}
		overlayManager.remove(currentStepOverlay);
		overlayManager.remove(withdrawOverlay);
		overlayManager.remove(nextStepOverlay);
		overlayManager.remove(adviceOverlay);
		keyManager.unregisterKeyListener(previousStepHotkey);
		keyManager.unregisterKeyListener(nextStepHotkey);
		mouseManager.unregisterMouseListener(guideMouseAdapter);

		panel = null;
		data = null;
	}

	@Subscribe
	public void onConfigChanged(ConfigChanged event)
	{
		if (!"boatyguide".equals(event.getGroup()))
		{
			return;
		}

		if ("applyStartAtBankNow".equals(event.getKey()) && config.applyStartAtBankNow() && data != null)
		{
			applyStartBankIfConfigured();
		}

		if ("resetProgressNow".equals(event.getKey()) && config.resetProgressNow() && data != null)
		{
			applyResetProgressIfConfigured();
		}

		if (panel != null && data != null)
		{
			refreshPanel();
		}
	}

	private void wirePanelActions()
	{
		panel.getPreviousButton().addActionListener(event -> handlePreviousStep());
		panel.getNextButton().addActionListener(event -> handleNextStep());
		panel.getCompleteBlockButton().addActionListener(event -> {
			guideStateManager.toggleCurrentBankCompleted(config.advanceToNextBankAfterBlockComplete());
			refreshPanel();
		});
	}

	private void refreshPanel()
	{
		GuideStep currentStep = guideStateManager.getCurrentStep();
		Optional<GuideBank> sidebarBank = guideStateManager.getSidebarBank();

		panel.render(
			currentStep,
			guideStateManager.getCurrentAdviceLines(),
			guideStateManager.getCurrentWithdrawLines(),
			guideStateManager.getRemainingStepsInCurrentBank(config.contextStepCount())
		);
		panel.setProgressActionState(
			config.showCompleteBlockButton(),
			guideStateManager.isCurrentBankCompleted()
		);
	}

	private void applyStartBankIfConfigured()
	{
		if (!config.applyStartAtBankNow())
		{
			return;
		}

		String startAtBankId = config.startAtBankId();
		if (startAtBankId == null || startAtBankId.isBlank())
		{
			configManager.setConfiguration("boatyguide", "applyStartAtBankNow", false);
			return;
		}

		boolean applied = guideStateManager.setProgressToBank(startAtBankId);
		configManager.setConfiguration("boatyguide", "applyStartAtBankNow", false);
		if (applied)
		{
			log.info("Applied start-bank progress to bank {}", startAtBankId);
		}
		else
		{
			log.warn("Unable to apply start-bank progress for bank {}", startAtBankId);
		}
	}

	private void applyResetProgressIfConfigured()
	{
		if (!config.resetProgressNow())
		{
			return;
		}

		guideStateManager.reset();
		configManager.setConfiguration("boatyguide", "resetProgressNow", false);
		log.info("Reset guide progress for current RuneLite profile");
	}

	private void handleNextStep()
	{
		if (data == null)
		{
			return;
		}

		guideStateManager.next();
		refreshPanel();
	}

	private void handlePreviousStep()
	{
		if (data == null)
		{
			return;
		}

		guideStateManager.previous();
		refreshPanel();
	}
}
