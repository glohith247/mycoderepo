## Wrapper Scripts for Mvnrelease

These scripts use `mvnrelease` to perform releases to the production
instance of Artifactory.


There is now also an explicit `mvnrelease1.7` for releasing using 1.7.
Going forward, this is preferred over plain `mvnrelease`, for clarity.

The real work is done in `lib/mvnrelease-generic`, which releases to
the rpm repo if it detects a rpm project being
rpm, and to maven repo otherwise.

To use these scripts, you'll need to put the following files in place
for your user (make them readable only to the release user):

**`~/.credentials.d/artifactory-devopsbuild-user`**
```
USERNAME=devopsbuild
PASSWORD="<password>"
```

**`~/.credentials.d/artifactory-mavenbuild-user`**
```
USERNAME=mavenbuild
PASSWORD="<password>"
```


### BUGS

Due to what appears to be a bug in the JGit library used by
mvnrelease, when creating a release of a Git project you must not be
in a Git repository when you invoke these scripts.  (For example, you
can't run these scripts from a checkout of this repository.)  If you
do, mvnrelease will clone the repository into the current directory
rather than switching to the proper destination work directory, and
will fail loudly when it doesn't find what it needs.

The version of JGit mvnrelease was using was 4.1.1; the behavior was
still there with 4.7.0.
