package com.boatyguide.guide;

import com.google.gson.Gson;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import javax.inject.Inject;
import javax.inject.Singleton;

@Singleton
public class GuideDataLoader
{
	private static final String GUIDE_RESOURCE = "/com/boatyguide/guide_data.json";

	private final Gson gson;

	@Inject
	public GuideDataLoader(Gson gson)
	{
		this.gson = gson;
	}

	public GuideData load() throws IOException
	{
		InputStream stream = GuideDataLoader.class.getResourceAsStream(GUIDE_RESOURCE);
		if (stream == null)
		{
			throw new IOException("Missing guide resource: " + GUIDE_RESOURCE);
		}

		try (InputStreamReader reader = new InputStreamReader(stream, StandardCharsets.UTF_8))
		{
			GuideData data = gson.fromJson(reader, GuideData.class);
			validate(data);
			data.buildIndexes();
			return data;
		}
	}

	private void validate(GuideData data) throws IOException
	{
		if (data == null)
		{
			throw new IOException("Guide data did not deserialize");
		}
		if (data.getEpisodes() == null || data.getEpisodes().isEmpty())
		{
			throw new IOException("Guide data contains no episodes");
		}
		if (data.getTotalSteps() <= 0)
		{
			throw new IOException("Guide data contains no steps");
		}
	}
}
