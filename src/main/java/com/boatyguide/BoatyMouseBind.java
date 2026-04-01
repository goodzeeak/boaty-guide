package com.boatyguide;

import java.awt.event.MouseEvent;

public enum BoatyMouseBind
{
	NONE("Not set", 0),
	MIDDLE("Middle click", MouseEvent.BUTTON2),
	BACK("Mouse button 4", 4),
	FORWARD("Mouse button 5", 5);

	private final String label;
	private final int button;

	BoatyMouseBind(String label, int button)
	{
		this.label = label;
		this.button = button;
	}

	public boolean matches(MouseEvent event)
	{
		return button != 0 && event.getButton() == button;
	}

	@Override
	public String toString()
	{
		return label;
	}
}
