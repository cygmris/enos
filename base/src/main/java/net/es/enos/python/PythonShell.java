/*
 * Copyright (c) 2014, Regents of the University of California  All rights reserved.
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 * 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

package net.es.enos.python;

import jline.console.ENOSConsoleReader;
import net.es.enos.boot.BootStrap;
import net.es.enos.kernel.exec.KernelThread;
import net.es.enos.kernel.users.User;
import net.es.enos.shell.ShellInputStream;;
import net.es.enos.shell.annotations.ShellCommand;


import java.io.*;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashMap;

import org.python.core.PyDictionary;
import org.python.util.PythonInterpreter;
import org.python.util.InteractiveConsole;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
// import org.python.util.JLineConsole;

import javax.print.DocFlavor;

/**
 * Created by lomax on 2/20/14.
 */
public class PythonShell {
    private static final Logger logger = LoggerFactory.getLogger(PythonShell.class);
    private static HashMap<InputStream,PyDictionary> locals = new HashMap<InputStream, PyDictionary>();

    @ShellCommand(
            name="python",
            forwardLines=false,
            shortHelp="Invoke interactive Python shell",
            longHelp="EOF in the shell exits the shell and returns control to the top-level\n" +
                    "ENOS shell."
    )
    public static void startPython (String[] args, InputStream in, OutputStream out, OutputStream err) {

        final Logger logger = LoggerFactory.getLogger(PythonShell.class);
        if (in instanceof ShellInputStream) {
            ((ShellInputStream) in).setDoCompletion(false);
        }
        PyDictionary sessionLocals;
        boolean isFirstSession = true;
        // Find or create locals
        synchronized (PythonShell.locals) {
            if (PythonShell.locals.containsKey(in)) {
                // Already has a locals created for this session, re-use
                sessionLocals = PythonShell.locals.get(in);
                isFirstSession = false;
            } else {
                // First python for this session. Create locals
                sessionLocals = new PyDictionary();
                PythonShell.locals.put(in,sessionLocals);
            }
        }
        logger.debug("Starting Python");
        if (isFirstSession) {
            // Run profile
            PythonShell.execProfile(sessionLocals,in,out,err);
        }

        if ((args != null) && (args.length > 1)) {
            // A program is provided.
            PythonInterpreter python = new PythonInterpreter(sessionLocals);
            python.setIn(in);
            python.setOut(out);
            python.setErr(err);
            logger.info("Executes file " + args[1] + " for user " + KernelThread.getCurrentKernelThread().getUser().getName());
            python.execfile(BootStrap.rootPath.toString() + args[1]);

        } else {
            // This is an interactive session
            try {
                InteractiveConsole console = new InteractiveConsole(sessionLocals);
                if (System.getProperty("python.home") == null) {
                    System.setProperty("python.home", "");
                }
                InteractiveConsole.initialize(System.getProperties(),
                        null, new String[0]);

                console.setOut(out);
                console.setErr(err);
                console.setIn(in);
                // Start the interactive session
                console.interact();
            } catch (Exception e) {
                // Nothing has to be done. This happens when the jython shell exits, obviously not too gracefully.
                e.printStackTrace();
            }
        }
        if (in instanceof ShellInputStream) {
            ((ShellInputStream) in).setDoCompletion(true);
        }

        logger.debug("Exiting Python");
    }

    private static void execProfile(PyDictionary locals, InputStream in, OutputStream out, OutputStream err) {
        User user = KernelThread.getCurrentKernelThread().getUser();
        Path homeDir = user.getHomePath();
        File profile = Paths.get(homeDir.toString(),"profile.py").toFile();
        if (!profile.exists()) {
            // No profile, nothing to do
            return;
        }
        // Execute the profile
        PythonInterpreter python = new PythonInterpreter(locals);
        python.setIn(in);
        python.setOut(out);
        python.setErr(err);
        logger.info("Executes file " + profile.toString() + " for user " + KernelThread.getCurrentKernelThread().getUser().getName());
        python.execfile(profile.toString());
    }

}
