from .weather_cog import Weather, WeatherCog

def setup(bot):
    bot.add_cog(WeatherCog(bot))