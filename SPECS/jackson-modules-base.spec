%bcond_with     jp_minimal

Name:           jackson-modules-base
Version:        2.14.1
Release:        2%{?dist}
Summary:        Jackson modules: Base
License:        Apache-2.0

URL:            https://github.com/FasterXML/jackson-modules-base
Source0:        %{url}/archive/%{name}-%{version}.tar.gz
Patch1:         0001-Expose-javax.security.auth-from-JDK-internals.patch

BuildRequires:  maven-local
BuildRequires:  mvn(cglib:cglib)
BuildRequires:  mvn(com.fasterxml.jackson.core:jackson-annotations) >= %{version}
BuildRequires:  mvn(com.fasterxml.jackson.core:jackson-core) >= %{version}
BuildRequires:  mvn(com.fasterxml.jackson.core:jackson-databind) >= %{version}
BuildRequires:  mvn(com.fasterxml.jackson:jackson-base:pom:) >= %{version}
BuildRequires:  mvn(com.google.code.maven-replacer-plugin:replacer)
BuildRequires:  mvn(jakarta.activation:jakarta.activation-api)
BuildRequires:  mvn(javax.xml.bind:jaxb-api)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  mvn(org.mockito:mockito-all)
BuildRequires:  mvn(org.ow2.asm:asm)

BuildArch:      noarch

%description
Jackson "base" modules: modules that build directly on databind,
and are not data-type, data format, or JAX-RS provider modules.

%package -n pki-%{name}
Summary: Jackson modules: Base
Obsoletes: %{name} < %{version}-%{release}
Conflicts: %{name} < %{version}-%{release}
Provides: %{name} = %{version}-%{release}

%description -n pki-%{name}
Jackson "base" modules: modules that build directly on databind,
and are not data-type, data format, or JAX-RS provider modules.

%package -n pki-jackson-module-jaxb-annotations
Summary: Support for using JAXB annotations as an alternative to "native" Jackson annotations
Obsoletes: jackson-module-jaxb-annotations < %{version}-%{release}
Conflicts: jackson-module-jaxb-annotations < %{version}-%{release}
Provides: jackson-module-jaxb-annotations = %{version}-%{release}

%description -n pki-jackson-module-jaxb-annotations
This Jackson extension module provides support for using JAXB (javax.xml.bind)
annotations as an alternative to native Jackson annotations. It is most often
used to make it easier to reuse existing data beans that used with JAXB
framework to read and write XML.

%prep
%setup -q -n %{name}-%{name}-%{version}
%patch1 -p1

%pom_remove_dep -r org.glassfish.jaxb:jaxb-runtime
%pom_remove_plugin "de.jjohannes:gradle-module-metadata-maven-plugin"

# no need for Java 9 module stuff
%pom_remove_plugin -r :moditect-maven-plugin

# move to "old" glassfish-jaxb-api artifactId
%pom_change_dep -r jakarta.xml.bind:jakarta.xml.bind-api javax.xml.bind:jaxb-api

# Disable bundling of asm
%pom_remove_plugin ":maven-shade-plugin" afterburner mrbean paranamer
%pom_xpath_remove "pom:properties/pom:osgi.private" mrbean paranamer

sed -i 's/\r//' mrbean/src/main/resources/META-INF/{LICENSE,NOTICE}
cp -p mrbean/src/main/resources/META-INF/{LICENSE,NOTICE} .

# Fix OSGi dependency
%pom_change_dep org.osgi:org.osgi.core org.osgi:osgi.core osgi

# NoClassDefFoundError: net/sf/cglib/core/CodeGenerationException
%pom_add_dep cglib:cglib:3.2.4:test guice

%pom_disable_module afterburner
%pom_disable_module guice
%pom_disable_module mrbean
%pom_disable_module osgi
%pom_disable_module paranamer
%pom_disable_module jakarta-xmlbind
%pom_disable_module blackbird
%pom_disable_module no-ctor-deser

# Allow javax,activation to be optional
%pom_add_plugin "org.apache.felix:maven-bundle-plugin" jaxb "
<configuration>
  <instructions>
    <Import-Package>javax.activation;resolution:=optional,*</Import-Package>
  </instructions>
</configuration>"

# This test fails since mockito was upgraded to 2.x
rm osgi/src/test/java/com/fasterxml/jackson/module/osgi/InjectOsgiServiceTest.java

%mvn_file ":{*}" jackson-modules/@1

%build
%mvn_build -s -j

%install
%mvn_install

%files -n pki-%{name} -f .mfiles-jackson-modules-base
%doc README.md release-notes
%license LICENSE NOTICE

%files -n pki-jackson-module-jaxb-annotations -f .mfiles-jackson-module-jaxb-annotations
%doc jaxb/README.md jaxb/release-notes
%license LICENSE NOTICE

%changelog
* Wed Nov 23 2022 Chris Kelley <ckelley@redhat.com> - 2.14.1-1
- Update to version 2.14.1
- Resolves: #2070122

* Wed Sep 22 2021 Red Hat PKI Team <rhcs-maint@redhat.com> - 2.11.4-8
- Drop jaxb-runtime dependency

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 2.11.4-7
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri May 21 2021 Red Hat PKI Team <rhcs-maint@redhat.com> - 2.11.4-6
- Drop jackson-module-afterburner, jackson-module-guice, jackson-module-mrbean,
  jackson-module-osgi, jackson-module-paranamer, and jackson-module-javadoc

* Wed Apr 28 2021 Red Hat PKI Team <rhcs-maint@redhat.com> - 2.11.4-5
- Add Obsoletes and Conflicts

* Fri Apr 23 2021 Red Hat PKI Team <rhcs-maint@redhat.com> - 2.11.4-4
- Rename subpackages to pki-jackson

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 2.11.4-3
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.11.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 18 2021 Fabio Valentini <decathorpe@gmail.com> - 2.11.4-1
- Update to version 2.11.4.

* Wed Oct 14 2020 Fabio Valentini <decathorpe@gmail.com> - 2.11.3-1
- Update to version 2.11.3.

* Sat Aug 08 2020 Fabio Valentini <decathorpe@gmail.com> - 2.11.2-1
- Update to version 2.11.2.

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.11.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 10 2020 Jiri Vanek <jvanek@redhat.com> - 2.11.1-2
- Rebuilt for JDK-11, see https://fedoraproject.org/wiki/Changes/Java11

* Mon Jul 06 2020 Fabio Valentini <decathorpe@gmail.com> - 2.11.1-1
- Update to version 2.11.1.

* Mon May 25 2020 Fabio Valentini <decathorpe@gmail.com> - 2.11.0-1
- Update to version 2.11.0.

* Fri May 08 2020 Fabio Valentini <decathorpe@gmail.com> - 2.10.4-1
- Update to version 2.10.4.

* Tue Mar 03 2020 Fabio Valentini <decathorpe@gmail.com> - 2.10.3-1
- Update to version 2.10.3.

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.10.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jan 17 2020 Fabio Valentini <decathorpe@gmail.com> - 2.10.2-1
- Update to version 2.10.2.

* Wed Nov 13 2019 Fabio Valentini <decathorpe@gmail.com> - 2.10.1-1
- Update to version 2.10.1.

* Tue Oct 08 2019 Fabio Valentini <decathorpe@gmail.com> - 2.10.0-1
- Update to version 2.10.0.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sun Mar 17 2019 Mat Booth <mat.booth@redhat.com> - 2.9.8-2
- Make the OSGi dep on javax.activation optional

* Wed Feb 06 2019 Mat Booth <mat.booth@redhat.com> - 2.9.8-1
- Update to latest upstream release

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jan 11 2019 Mat Booth <mat.booth@redhat.com> - 2.9.4-5
- Avoid running test that fails since Mockito 2.x

* Wed Aug 22 2018 Mat Booth <mat.booth@redhat.com> - 2.9.4-4
- Allow conditional building of some extra modules

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jan 24 2018 Mat Booth <mat.booth@redhat.com> - 2.9.4-1
- Update to latest upstream release

* Tue Jan 23 2018 Mat Booth <mat.booth@redhat.com> - 2.9.3-2
- Properly obsolete jackson-module-jaxb-annotations-javadoc package

* Tue Jan 23 2018 Mat Booth <mat.booth@redhat.com> - 2.9.3-1
- Update to latest upstream release
- Obsoletes standalone jaxb-annotations package now provided by this package

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Sep 20 2016 gil cattaneo <puntogil@libero.it> 2.7.6-2
- fix some rpmlint problems 

* Mon Aug 22 2016 gil cattaneo <puntogil@libero.it> 2.7.6-1
- initial rpm

