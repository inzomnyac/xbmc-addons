# Introduction #
To make the end-user experience seamless, skinners can add support for [Cinema Experience](CinemaExperienceIntro.md) directly to their skins.


# Details #
We recommend that you add a button to DialogVideoInfo.xml similar to this (taken from [Night skin](http://forum.xbmc.org/showthread.php?t=82628))

```
<control type="button" id="13">
    <description>Home Theatre</description>
    <include>ButtonInfoDialogsCommonValues</include>
    <label>Cinema</label>
    <onclick>Playlist.Clear</onclick>
    <onclick>Dialog.Close(MovieInformation)</onclick>
    <onclick>XBMC.RunScript(script.cinema.experience)</onclick>
    <visible>system.hasaddon(script.cinema.experience) + Container.Content(movies)</visible>
</control>
```

# Additional Discussion #
On the XBMC Forums, mcborzu started a discussion regarding the recommended way for skinners to integrate this script into their themes: http://forum.xbmc.org/showthread.php?t=87945

Also on the XBMC Forums, Harro posts a mod for Confluence to add support for Cinema Experience: http://forum.xbmc.org/showthread.php?t=87883&highlight=Cinema+Experience