package com.pushio.jenkins.plugin;

import hudson.EnvVars;
import hudson.Extension;
import hudson.Launcher;
import hudson.model.*;
import hudson.tasks.BuildStepDescriptor;
import hudson.tasks.BuildStepMonitor;
import hudson.tasks.Notifier;
import hudson.tasks.Publisher;

import java.io.PrintStream;
import java.lang.String;
import java.lang.InterruptedException;
import java.io.IOException;
import java.util.logging.Logger;

import org.apache.commons.lang.StringUtils;
import org.kohsuke.stapler.DataBoundConstructor;
import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpException;
import org.apache.commons.httpclient.NameValuePair;
import org.apache.commons.httpclient.methods.PostMethod;

/**
 * Created with IntelliJ IDEA.
 * User: Jay Graves
 * Date: 7/29/12
 * Time: 1:18 PM
 */
public class PushIOBuildNotifier extends Notifier {

    private final String appID;
    private final String serviceSecret;
    private final String pushCategory;
    private final String payload;

    @DataBoundConstructor
    public PushIOBuildNotifier(String appID, String serviceSecret, String pushCategory, String payload) {
        super();

        this.appID = appID;
        this.serviceSecret = serviceSecret;
        this.pushCategory = pushCategory;
        this.payload = payload;
    }

    public String getAppID() {
        return appID;
    }

    public String getServiceSecret() {
        return serviceSecret;
    }

    public String getPushCategory() {
        return pushCategory;
    }

    public String getPayload() {
        return payload;
    }

    protected void log(final PrintStream logger, final String message) {
        logger.println(StringUtils.defaultString(getDescriptor().getDisplayName()) + " " + message);
    }

    @Override
    public BuildStepMonitor getRequiredMonitorService() {
        return BuildStepMonitor.BUILD;
    }

    @Override
    public boolean perform(AbstractBuild<?, ?> build, Launcher launcher, BuildListener listener) throws InterruptedException, IOException {
        EnvVars vars = build.getEnvironment(listener);

        if (build.getResult().isWorseOrEqualTo(Result.FAILURE))
            return false;

        HttpClient client = new HttpClient();

        String url = "https://manage.push.io/api/v1/notify_app/"+vars.expand(appID)+"/"+vars.expand(serviceSecret);

        PostMethod method = new PostMethod(url);
        method.setParameter("payload", vars.expand(payload));
        method.setParameter("tag_query", vars.expand(pushCategory));
        client.executeMethod(method);

        String response = method.getResponseBodyAsString();
        log(listener.getLogger(), "PushIO response"+response);

        method.releaseConnection();
        return true;
    }

    @Extension
    public static class DescriptorImpl extends BuildStepDescriptor<Publisher> {
        public DescriptorImpl() {
            load();
        }

        @Override
        public String getDisplayName(){
            return "PushIO Notification";
        }

        @Override
        public boolean isApplicable(Class<? extends AbstractProject> aClass) {
            return true;
        }
    }
}
