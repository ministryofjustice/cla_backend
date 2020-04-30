{% load i18n %}<?xml version='1.0' encoding='UTF-8' standalone='no'?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yEd 3.19.1.1-->
  <key for="port" id="d0" yfiles.type="portgraphics"/>
  <key for="port" id="d1" yfiles.type="portgeometry"/>
  <key for="port" id="d2" yfiles.type="portuserdata"/>
  <key attr.name="body" attr.type="string" for="node" id="d3">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="help" attr.type="string" for="node" id="d4">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="heading" attr.type="string" for="node" id="d5">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="outcome" attr.type="string" for="node" id="d6">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="title" attr.type="string" for="node" id="d7">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="context:test" attr.type="string" for="node" id="d8">
    <default xml:space="preserve"/>
  </key>
  <key attr.name="context:xml" for="node" id="d9">
    <default/>
  </key>
  <key attr.name="order" attr.type="int" for="node" id="d10">
    <default xml:space="preserve">9999</default>
  </key>
  <key attr.name="permanent_id" attr.type="string" for="node" id="d11"/>
  <key attr.name="data_safety" attr.type="string" for="node" id="d12">
    <default xml:space="preserve">false</default>
  </key>
  <key attr.name="url" attr.type="string" for="node" id="d13"/>
  <key attr.name="description" attr.type="string" for="node" id="d14"/>
  <key for="node" id="d15" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d16" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d17"/>
  <key attr.name="description" attr.type="string" for="edge" id="d18"/>
  <key for="edge" id="d19" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0" yfiles.foldertype="group">
      <data key="d11" xml:space="preserve">n43</data>
      <data key="d13" xml:space="preserve"/>
      <graph edgedefault="directed" id="n0:">
        <node id="n0::n0">
          <data key="d3" xml:space="preserve">{% trans "Clinical negligence" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Problems with your medical care and treatment" %}</data>
          <data key="d6" xml:space="preserve">f2f</data>
          <data key="d10" xml:space="preserve">1</data>
          <data key="d11" xml:space="preserve">n43n0</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n1">
          <data key="d3" xml:space="preserve">{% trans "Community care" %}</data>
          <data key="d4" xml:space="preserve">{% trans "You’re unhappy with the care you or a relative are getting due to disability, age or special educational needs eg in a care home or your own home" %}</data>
          <data key="d6" xml:space="preserve">f2f</data>
          <data key="d10" xml:space="preserve">2</data>
          <data key="d11" xml:space="preserve">n43n1</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n2">
          <data key="d3" xml:space="preserve">{% trans "Debt" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Bankruptcy, repossession, mortgage debt that is putting your home at risk" %}</data>
          <data key="d5" xml:space="preserve">{% trans "Choose the option that best describes your debt problem" %}</data>
          <data key="d10" xml:space="preserve">3</data>
          <data key="d11" xml:space="preserve">n43n2</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n3">
          <data key="d3" xml:space="preserve">{% trans "Domestic abuse" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Abuse at home (psychological, physical, financial, sexual or emotional), child abuse, harassment by an ex-partner, forced marriage" %}</data>
          <data key="d5" xml:space="preserve">{% trans "Choose the option that best describes your personal situation" %}</data>
          <data key="d10" xml:space="preserve">4</data>
          <data key="d11" xml:space="preserve">n43n3</data>
          <data key="d12" xml:space="preserve">true</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n4">
          <data key="d3" xml:space="preserve">{% trans "Discrimination" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Being treated unfairly because of eg your race, gender or sexual orientation" %}</data>
          <data key="d5" xml:space="preserve">{% trans "On what grounds have you been discriminated against?" %}</data>
          <data key="d10" xml:space="preserve">5</data>
          <data key="d11" xml:space="preserve">n43n4</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n5">
          <data key="d3" xml:space="preserve">{% trans "Education" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Special educational needs, problems with school places, exclusions, learning difficulties" %}</data>
          <data key="d5" xml:space="preserve">{% trans "What is your education problem about?" %}</data>
          <data key="d10" xml:space="preserve">6</data>
          <data key="d11" xml:space="preserve">n43n5</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n6">
          <data key="d3" xml:space="preserve">{% trans "Employment" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Being treated unfairly at work, unfair dismissal, employment tribunals" %}</data>
          <data key="d5" xml:space="preserve">{% trans "What is your employment problem about?" %}</data>
          <data key="d10" xml:space="preserve">7</data>
          <data key="d11" xml:space="preserve">n43n6</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n7">
          <data key="d3" xml:space="preserve">{% trans "Housing" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Eviction, homelessness, losing your rented home, rent arrears, harassment by a landlord or neighbour, health and safety issues with your home" %}</data>
          <data key="d5" xml:space="preserve">{% trans "Choose the option that best describes your housing situation" %}</data>
          <data key="d10" xml:space="preserve">9</data>
          <data key="d11" xml:space="preserve">n43n7</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n8">
          <data key="d3" xml:space="preserve">{% trans "Immigration and asylum" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Applying for asylum or permission to stay in the UK, including for victims of human trafficking" %}</data>
          <data key="d5" xml:space="preserve">{% trans "Choose the option that best describes your situation" %}</data>
          <data key="d10" xml:space="preserve">10</data>
          <data key="d11" xml:space="preserve">n43n8</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n9">
          <data key="d3" xml:space="preserve">{% trans "Mental health" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Help with mental health and mental capacity legal issues" %}</data>
          <data key="d6" xml:space="preserve">f2f</data>
          <data key="d10" xml:space="preserve">11</data>
          <data key="d11" xml:space="preserve">n43n9</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n10">
          <data key="d3" xml:space="preserve">{% trans "Personal injury" %}</data>
          <data key="d4" xml:space="preserve">{% trans "An accident that was not your fault" %}</data>
          <data key="d6" xml:space="preserve">f2f</data>
          <data key="d10" xml:space="preserve">12</data>
          <data key="d11" xml:space="preserve">n43n10</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n11">
          <data key="d3" xml:space="preserve">{% trans "Public law" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Taking legal action against a public body, like your local council" %}</data>
          <data key="d6" xml:space="preserve">f2f</data>
          <data key="d10" xml:space="preserve">13</data>
          <data key="d11" xml:space="preserve">n43n11</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n12">
          <data key="d3" xml:space="preserve">{% trans "Trouble with the police and other public authorities" %}</data>
          <data key="d4" xml:space="preserve">{% trans "You’ve been treated wrongly by the police or other authorities with the power to detain, imprison or prosecute you" %}</data>
          <data key="d10" xml:space="preserve">14</data>
          <data key="d11" xml:space="preserve">n43n12</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n13">
          <data key="d3" xml:space="preserve">{% trans "Welfare benefits" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Problems with your benefits, appealing a decision about your benefits" %}</data>
          <data key="d5" xml:space="preserve">{% trans "What is your benefits problem about?" %}</data>
          <data key="d10" xml:space="preserve">15</data>
          <data key="d11" xml:space="preserve">n43n13</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n14">
          <data key="d3" xml:space="preserve">{% trans "Family" %}</data>
          <data key="d4" xml:space="preserve">{% trans "Divorce, separation, dissolution, financial arrangements, family mediation, arrangements for your children, children being taken into care, child abduction" %}</data>
          <data key="d5" xml:space="preserve">{% trans "What is your family problem about?" %}</data>
          <data key="d10" xml:space="preserve">8</data>
          <data key="d11" xml:space="preserve">n43n14</data>
          <data key="d12" xml:space="preserve">true</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n0::n15">
          <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
          <data key="d5" xml:space="preserve">{% trans "What is your problem about?" %}</data>
          <data key="d11" xml:space="preserve">n60</data>
          </node>
      </graph>
    </node>
    <node id="n1">
      <data key="d3" xml:space="preserve">{% trans "You’re a home owner, and you’re at risk of losing your home due to bankruptcy, mortgage debt or repossession" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n0</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n2">
      <data key="d3" xml:space="preserve">{% trans "You owe money (for example, bank loans, credit card debt) but this is not putting your home at risk" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n3</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n3">
      <data key="d5" xml:space="preserve">{% trans "Choose one of the options" %}</data>
      <data key="d8" xml:space="preserve">testcontext</data>
      <data key="d11" xml:space="preserve">start</data>
      <data key="d13" xml:space="preserve"/>
      <data key="d14" xml:space="preserve">Public Site Diagnosis</data>
      </node>
    <node id="n4">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d6" xml:space="preserve">call_me_back</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n18</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n5">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n19</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n6">
      <data key="d3" xml:space="preserve">{% trans "Benefits appeal" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You want to appeal a decision about your benefits" %}</data>
      <data key="d5" xml:space="preserve">{% trans "You want to appeal a benefits decision:" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n20</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n7">
      <data key="d3" xml:space="preserve">{% trans "Permission to appeal refused" %}</data>
      <data key="d4" xml:space="preserve">{% trans "A first-tier tribunal has refused you permission to appeal your benefits decision in the Upper Tribunal and you want advice about how to appeal this decision" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n21</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n8">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n22</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n9">
      <data key="d3" xml:space="preserve">{% trans "Age" %}</data>
      <data key="d5" xml:space="preserve">{% trans "How old are you?" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n23</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n10">
      <data key="d3" xml:space="preserve">{% trans "Disability" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n24</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n11">
      <data key="d3" xml:space="preserve">{% trans "Gender, gender reassignment or sexual orientation" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n25</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n12">
      <data key="d3" xml:space="preserve">{% trans "Marriage or civil partnership" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">4</data>
      <data key="d11" xml:space="preserve">n26</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n13">
      <data key="d3" xml:space="preserve">{% trans "Pregnancy or maternity" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n27</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n14">
      <data key="d3" xml:space="preserve">{% trans "Race" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Including nationality, citizenship, ethnicity or national origin" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">6</data>
      <data key="d11" xml:space="preserve">n28</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n15">
      <data key="d3" xml:space="preserve">{% trans "Religion, belief, or lack of religion or belief" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">7</data>
      <data key="d11" xml:space="preserve">n29</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n16">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n30</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n17">
      <data key="d3" xml:space="preserve">{% trans "At work" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n31</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n18">
      <data key="d3" xml:space="preserve">{% trans "While you were using a service" %}</data>
      <data key="d4" xml:space="preserve">{% trans "For example, having a meal in a restaurant or getting access to a shop" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n32</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n19">
      <data key="d3" xml:space="preserve">{% trans "In an association" %}</data>
      <data key="d4" xml:space="preserve">{% trans "For example, a private club or political organisation" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">4</data>
      <data key="d11" xml:space="preserve">n33</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n20">
      <data key="d3" xml:space="preserve">{% trans "When someone was carrying out a public function" %}</data>
      <data key="d4" xml:space="preserve">{% trans "For example, a police officer carrying out a search as part of a criminal investigation" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n34</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n21">
      <data key="d3" xml:space="preserve">{% trans "At school or college" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">6</data>
      <data key="d11" xml:space="preserve">n35</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n22">
      <data key="d3" xml:space="preserve">{% trans "At university" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Or other further education or higher education institution" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">7</data>
      <data key="d11" xml:space="preserve">n36</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n23">
      <data key="d3" xml:space="preserve">{% trans "18 or over" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n37</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n24">
      <data key="d3" xml:space="preserve">{% trans "Under 18" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Where did the discrimination occur?" %}</data>
      <data key="d6" xml:space="preserve">contact</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n38</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n25">
      <data key="d3" xml:space="preserve">{% trans "A child in care or a care leaver - or you are a foster carer" %}</data>
      <data key="d6" xml:space="preserve">eligible</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n39</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n26">
      <data key="d3" xml:space="preserve">{% trans "Special educational needs" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You have (or your child has) special educational needs - this includes problems about transport, being out of school or being in a pupil referral unit" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n40</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n27">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d4" xml:space="preserve">{% trans "For example admissions or exclusions" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n41</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n28">
      <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n42</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n29">
      <data key="d3" xml:space="preserve">{% trans "Domestic abuse" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You want to protect yourself or your children against domestic abuse (including psychological, physical, financial, sexual or emotional abuse)" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you or your children at immediate risk of harm?" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n44</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n30">
      <data key="d3" xml:space="preserve">{% trans "Enforcing an injunction" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Your partner or ex-partner is ignoring an injunction you have taken out against them" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you at immediate risk of harm?" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n45</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n31">
      <data key="d3" xml:space="preserve">{% trans "Harassment" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You are being harassed by  a partner, ex-partner or family member" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you at immediate risk of harm?" %}</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n46</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n32">
      <data key="d3" xml:space="preserve">{% trans "Contesting an injunction" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You want to contest an injunction that has been taken out against you" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">4</data>
      <data key="d11" xml:space="preserve">n47</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n33">
      <data key="d3" xml:space="preserve">{% trans "Forced marriage" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You want advice about forced marriage" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n48</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n34">
      <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n49</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n35">
      <data key="d3" xml:space="preserve">{% trans "Children being taken into care and adoption" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Your local council is involved" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Is the local council trying to take your child into care?" %}</data>
      <data key="d10" xml:space="preserve">6</data>
      <data key="d11" xml:space="preserve">n50</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n36">
      <data key="d3" xml:space="preserve">{% trans "Child abduction" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You want advice about child abduction" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Select the option that best describes your situation" %}</data>
      <data key="d6" xml:space="preserve">contact</data>
      <data key="d10" xml:space="preserve">7</data>
      <data key="d11" xml:space="preserve">n52</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n37">
      <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n53</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n38">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d6" xml:space="preserve">eligible</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n54</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n39">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n55</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n40">
      <data key="d3" xml:space="preserve">{% trans "Divorce, separation or dissolution" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Choose the option that best describes your situation" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n56</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n41">
      <data key="d3" xml:space="preserve">{% trans "Financial settlement" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Following a divorce or separation" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Choose the option that best describes your situation" %}</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n58</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n42">
      <data key="d3" xml:space="preserve">{% trans "Family mediation" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You’re looking to start family mediation or you’re seeking legal advice in support of it" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Have you already started family mediation? (This includes cases that have already finished)" %}</data>
      <data key="d10" xml:space="preserve">4</data>
      <data key="d11" xml:space="preserve">n59</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n43">
      <data key="d3" xml:space="preserve">{% trans "You are under 18" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n61</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n44">
      <data key="d3" xml:space="preserve">{% trans "Domestic abuse" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You or your children have suffered domestic abuse, or your abuser has a criminal conviction" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you at immediate risk of harm?" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n62</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n45">
      <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n99</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n46">
      <data key="d3" xml:space="preserve">{% trans "International Family Maintenance" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You’re seeking advice about International Family Maintenance, to enforce a maintenance order made outside the UK" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n64</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n47">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n65</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n48">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n66</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n49">
      <data key="d3" xml:space="preserve">{% trans "You’re living in rented accommodation" %}</data>
      <data key="d5" xml:space="preserve">{% trans "What is your housing problem about?" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n67</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n50">
      <data key="d3" xml:space="preserve">{% trans "You are homeless" %}</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n68</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n51">
      <data key="d3" xml:space="preserve">{% trans "Any other housing problem" %}</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n69</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n52">
      <data key="d3" xml:space="preserve">{% trans "Becoming homeless" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You are at risk of becoming homeless within 56 days and you want to make an application to your local council to stop your home being taken away from you" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n70</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n53">
      <data key="d3" xml:space="preserve">{% trans "Eviction" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You are being evicted from your home" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Select the option that best describes your situation" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n71</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n54">
      <data key="d3" xml:space="preserve">{% trans "Harassment" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Your landlord or neighbour is harassing you" %}</data>
      <data key="d10" xml:space="preserve">4</data>
      <data key="d11" xml:space="preserve">n72</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n55">
      <data key="d3" xml:space="preserve">{% trans "Contesting an injunction for antisocial behaviour" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Your landlord has taken out an injunction against you or someone who lives with you" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Your landlord is:" %}</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n73</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n56">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n74</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n57" yfiles.foldertype="group">
      <data key="d11" xml:space="preserve">n82</data>
      <data key="d13" xml:space="preserve"/>
      <graph edgedefault="directed" id="n57:">
        <node id="n57::n0">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">clinneg</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n0</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n1">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">commcare</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n1</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n2">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">debt</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n2</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n3">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">debt</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n3</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n4">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">violence</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n4</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n5">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">violence</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n5</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n6">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">discrimination</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n6</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n7">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">discrimination</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n7</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n8">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">education</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n8</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n9">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">education</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n9</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n10">
          <data key="d3" xml:space="preserve">CONTACT</data>
          <data key="d4" xml:space="preserve">{% trans "Problem relates to a child in care, or a care leaver, or user is a foster carer" %}</data>
          <data key="d7" xml:space="preserve">CONTACT</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">education</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n10</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n11">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">employment</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n11</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n12">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">housing</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n12</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n13">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">housing</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n13</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n14">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">immigration</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n14</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n15">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">housing</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n15</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n16">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">mentalhealth</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n16</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n17">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">pi</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n17</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n18">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">publiclaw</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n18</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n19">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">family</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n19</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n20">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">family</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n20</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n21">
          <data key="d3" xml:space="preserve">CONTACT</data>
          <data key="d4" xml:space="preserve">{% trans "Council is trying to take user’s child into care" %}</data>
          <data key="d7" xml:space="preserve">CONTACT</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">family</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n21</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n22">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">aap</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n22</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n23">
          <data key="d3" xml:space="preserve">INSCOPE</data>
          <data key="d7" xml:space="preserve">INSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">benefits</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n23</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n24">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">welfare-benefits</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n24</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n25">
          <data key="d3" xml:space="preserve">CONTACT</data>
          <data key="d4" xml:space="preserve">{% trans "User is at immediate risk of harm" %}</data>
          <data key="d7" xml:space="preserve">CONTACT</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">violence</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n25</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n26">
          <data key="d3" xml:space="preserve">CONTACT</data>
          <data key="d4" xml:space="preserve">{% trans "User is under 18 years old" %}</data>
          <data key="d7" xml:space="preserve">CONTACT</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">discrimination</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n26</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n27">
          <data key="d3" xml:space="preserve">CONTACT</data>
          <data key="d4" xml:space="preserve">{% trans "User is under 18 years old" %}</data>
          <data key="d7" xml:space="preserve">CONTACT</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">family</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n27</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n28">
          <data key="d3" xml:space="preserve">CONTACT</data>
          <data key="d4" xml:space="preserve">{% trans "User is living outside the UK but user’s child has been taken to the UK" %}</data>
          <data key="d7" xml:space="preserve">CONTACT</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">family</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n28</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n29">
          <data key="d3" xml:space="preserve">MEDIATION</data>
          <data key="d7" xml:space="preserve">MEDIATION</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">family</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n29</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n30">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">debt</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n30</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n31">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">housing</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n31</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n32">
          <data key="d3" xml:space="preserve">CONTACT</data>
          <data key="d4" xml:space="preserve">{% trans "User is at immediate risk of harm" %}</data>
          <data key="d7" xml:space="preserve">CONTACT</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">violence</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n32</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n33">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">employment</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n33</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n34">
          <data key="d3" xml:space="preserve">INELIGIBLE</data>
          <data key="d7" xml:space="preserve">INELIGIBLE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">other</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n121</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n35">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">other</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n120</data>
          <data key="d13" xml:space="preserve"/>
          </node>
        <node id="n57::n36">
          <data key="d3" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d7" xml:space="preserve">OUTOFSCOPE</data>
          <data key="d9" xml:space="preserve">
            <context xmlns="" xml:space="preserve">
<category xml:space="preserve">housing</category>
</context>
          </data>
          <data key="d11" xml:space="preserve">n82n152</data>
          <data key="d13" xml:space="preserve"/>
          </node>
      </graph>
    </node>
    <node id="n58">
      <data key="d3" xml:space="preserve">{% trans "Losing your accommodation" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You’re losing your accommodation because UK Visas and Immigration (UKVI) is refusing to support you or is withdrawing its support from you" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n83</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n59">
      <data key="d3" xml:space="preserve">{% trans "You want advice on seeking asylum or appealing a decision about your asylum" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n84</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n60">
      <data key="d3" xml:space="preserve">{% trans "None of the above" %}</data>
      <data key="d11" xml:space="preserve">n85</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n61">
      <data key="d3" xml:space="preserve">{% trans "You’re a victim of domestic violence" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you at immediate risk of harm?" %}</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n86</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n62">
      <data key="d3" xml:space="preserve">{% trans "Your home is in a serious state of disrepair" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Does this create a serious risk of illness or injury?" %}</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n89</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n63">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n90</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n64">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n91</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n65">
      <data key="d3" xml:space="preserve">{% trans "You own your own home" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you at risk of losing your home because of bankruptcy, repossession or mortgage debt?" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n92</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n66">
      <data key="d3" xml:space="preserve">{% trans "A neighbour" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n93</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n67">
      <data key="d3" xml:space="preserve">{% trans "Domestic abuse or harassment" %}</data>
      <data key="d4" xml:space="preserve">{% trans "Abuse at home (including psychological, physical, financial, sexual or emotional abuse), child abuse, harassment" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Select the option that best describes your situation" %}</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n97</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n68">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d6" xml:space="preserve">INSCOPE</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n100</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n69">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d6" xml:space="preserve">INELIGIBLE</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n101</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n70">
      <data key="d3" xml:space="preserve">{% trans "Female genital mutilation" %}</data>
      <data key="d4" xml:space="preserve">{% trans "You’re worried that you may become a victim of female genital mutilation" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you at immediate risk of harm?" %}</data>
      <data key="d10" xml:space="preserve">6</data>
      <data key="d11" xml:space="preserve">n104</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n71">
      <data key="d3" xml:space="preserve">{% trans "Disputes over children" %}</data>
      <data key="d5" xml:space="preserve">{% trans "What kind of dispute is it?" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n105</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n72">
      <data key="d3" xml:space="preserve">{% trans "You’re in a dispute with your ex-partner over your children" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Select the option that best describes your situation" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n106</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n73">
      <data key="d3" xml:space="preserve">{% trans "You’re a relative (for example, a grandparent) seeking contact with a child in your family" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Is the child a victim of child abuse within the family?" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n107</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n74">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n108</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n75">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n109</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n76">
      <data key="d3" xml:space="preserve">{% trans "Other" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d7" xml:space="preserve">Other</data>
      <data key="d11" xml:space="preserve">n111</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n77">
      <data key="d3" xml:space="preserve">{% trans "At home (in rented accommodation)" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d7" xml:space="preserve">Other</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n112</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n78">
      <data key="d3" xml:space="preserve">{% trans "You’re an asylum seeker applying for accommodation" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n114</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n79">
      <data key="d3" xml:space="preserve">{% trans "You’re an asylum seeker applying for accommodation" %}</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n115</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n80">
      <data key="d3" xml:space="preserve">{% trans "Yes" %}</data>
      <data key="d6" xml:space="preserve">call_me_back</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n116</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n81">
      <data key="d3" xml:space="preserve">{% trans "No" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n117</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n82">
      <data key="d3" xml:space="preserve">{% trans "You’re losing your accommodation because UK Visas and Immigration (UKVI) is refusing to support you or is withdrawing its support from you" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n118</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n83">
      <data key="d3" xml:space="preserve">{% trans "You’re living in rented accommodation and you’re being evicted because of a debt to your landlord" %}</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n1</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n84">
      <data key="d3" xml:space="preserve">{% trans "Any other problem to do with divorce, separation or dissolution" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d11" xml:space="preserve">n63</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n85">
      <data key="d3" xml:space="preserve">{% trans "You’re a victim of human trafficking or modern slavery" %}</data>
      <data key="d11" xml:space="preserve">n149</data>
      </node>
    <node id="n86">
      <data key="d3" xml:space="preserve">{% trans "You’re a victim of human trafficking or modern slavery" %}</data>
      <data key="d5" xml:space="preserve">{% trans "Are you at immediate risk of harm?" %}</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n88</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n87">
      <data key="d3" xml:space="preserve">{% trans "On a point of law in the Upper Tribunal, Court of Appeal or Supreme Court" %}</data>
      <data key="d11" xml:space="preserve">n87</data>
      </node>
    <node id="n88">
      <data key="d3" xml:space="preserve">{% trans "In the first-tier tribunal" %}</data>
      <data key="d11" xml:space="preserve">n94</data>
      </node>
    <node id="n89">
      <data key="d3" xml:space="preserve">{% trans "A social housing landlord" %}</data>
      <data key="d4" xml:space="preserve">{% trans "For example, housing association, council housing" %}</data>
      <data key="d6" xml:space="preserve">means_test</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n11</data>
      </node>
    <node id="n90">
      <data key="d3" xml:space="preserve">{% trans "A private landlord" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n12</data>
      </node>
    <node id="n91">
      <data key="d3" xml:space="preserve">{% trans "You need advice about being a victim of abuse as a child or vulnerable adult (or on behalf of a victim)" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">1</data>
      <data key="d11" xml:space="preserve">n60n1</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n92">
      <data key="d3" xml:space="preserve">{% trans "You’ve been barred, or are being barred, from working with children or vulnerable adults and you want to appeal" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">2</data>
      <data key="d11" xml:space="preserve">n60n2</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n93">
      <data key="d3" xml:space="preserve">{% trans "Someone has applied for a gang injunction against you" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">3</data>
      <data key="d11" xml:space="preserve">n60n3</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n94">
      <data key="d3" xml:space="preserve">{% trans "Someone has applied for an injunction for antisocial behaviour against you or someone you live with" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">4</data>
      <data key="d11" xml:space="preserve">n60n4</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n95">
      <data key="d3" xml:space="preserve">{% trans "You need advice about being the victim of a sexual offence (or on behalf of a victim)" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">5</data>
      <data key="d11" xml:space="preserve">n60n5</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n96">
      <data key="d3" xml:space="preserve">{% trans "You need advice about an inquest into the death of a family member" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">6</data>
      <data key="d11" xml:space="preserve">n60n6</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n97">
      <data key="d3" xml:space="preserve">{% trans "You’re seeking an injunction because of nuisance caused by environmental pollution" %}</data>
      <data key="d6" xml:space="preserve">f2f</data>
      <data key="d10" xml:space="preserve">7</data>
      <data key="d11" xml:space="preserve">n60n7</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <node id="n98">
      <data key="d3" xml:space="preserve">{% trans "Any other problem" %}</data>
      <data key="d6" xml:space="preserve">ineligible</data>
      <data key="d10" xml:space="preserve">8</data>
      <data key="d11" xml:space="preserve">n60n8</data>
      <data key="d13" xml:space="preserve"/>
      </node>
    <edge id="e0" source="n3" target="n0::n0">
      </edge>
    <edge id="e1" source="n3" target="n0::n1">
      </edge>
    <edge id="e2" source="n3" target="n0::n2">
      </edge>
    <edge id="e3" source="n3" target="n0::n3">
      </edge>
    <edge id="e4" source="n3" target="n0::n4">
      </edge>
    <edge id="e5" source="n3" target="n0::n5">
      </edge>
    <edge id="e6" source="n3" target="n0::n6">
      </edge>
    <edge id="e7" source="n3" target="n0::n7">
      </edge>
    <edge id="e8" source="n3" target="n0::n8">
      </edge>
    <edge id="e9" source="n3" target="n0::n9">
      </edge>
    <edge id="e10" source="n3" target="n0::n10">
      </edge>
    <edge id="e11" source="n3" target="n0::n11">
      </edge>
    <edge id="e12" source="n3" target="n0::n12">
      </edge>
    <edge id="e13" source="n3" target="n0::n13">
      </edge>
    <edge id="e14" source="n0::n2" target="n1">
      </edge>
    <edge id="e15" source="n0::n2" target="n2">
      </edge>
    <edge id="e16" source="n0::n13" target="n6">
      </edge>
    <edge id="e17" source="n0::n13" target="n7">
      </edge>
    <edge id="e18" source="n0::n13" target="n8">
      </edge>
    <edge id="n0::e0" source="n0::n13" target="n0::n4">
      </edge>
    <edge id="e19" source="n0::n4" target="n9">
      </edge>
    <edge id="e20" source="n0::n4" target="n10">
      </edge>
    <edge id="e21" source="n0::n4" target="n11">
      </edge>
    <edge id="e22" source="n0::n4" target="n12">
      </edge>
    <edge id="e23" source="n0::n4" target="n13">
      </edge>
    <edge id="e24" source="n0::n4" target="n14">
      </edge>
    <edge id="e25" source="n0::n4" target="n15">
      </edge>
    <edge id="e26" source="n0::n4" target="n16">
      </edge>
    <edge id="e27" source="n15" target="n17">
      </edge>
    <edge id="e28" source="n15" target="n18">
      </edge>
    <edge id="e29" source="n15" target="n19">
      </edge>
    <edge id="e30" source="n15" target="n20">
      </edge>
    <edge id="e31" source="n15" target="n21">
      </edge>
    <edge id="e32" source="n15" target="n22">
      </edge>
    <edge id="e33" source="n15" target="n76">
      </edge>
    <edge id="e34" source="n14" target="n17">
      </edge>
    <edge id="e35" source="n14" target="n18">
      </edge>
    <edge id="e36" source="n14" target="n19">
      </edge>
    <edge id="e37" source="n14" target="n20">
      </edge>
    <edge id="e38" source="n14" target="n21">
      </edge>
    <edge id="e39" source="n14" target="n22">
      </edge>
    <edge id="e40" source="n14" target="n76">
      </edge>
    <edge id="e41" source="n13" target="n17">
      </edge>
    <edge id="e42" source="n13" target="n18">
      </edge>
    <edge id="e43" source="n13" target="n19">
      </edge>
    <edge id="e44" source="n13" target="n20">
      </edge>
    <edge id="e45" source="n13" target="n21">
      </edge>
    <edge id="e46" source="n13" target="n22">
      </edge>
    <edge id="e47" source="n13" target="n76">
      </edge>
    <edge id="e48" source="n12" target="n17">
      </edge>
    <edge id="e49" source="n12" target="n76">
      </edge>
    <edge id="e50" source="n11" target="n17">
      </edge>
    <edge id="e51" source="n11" target="n18">
      </edge>
    <edge id="e52" source="n11" target="n19">
      </edge>
    <edge id="e53" source="n11" target="n20">
      </edge>
    <edge id="e54" source="n11" target="n21">
      </edge>
    <edge id="e55" source="n11" target="n22">
      </edge>
    <edge id="e56" source="n11" target="n76">
      </edge>
    <edge id="e57" source="n10" target="n17">
      </edge>
    <edge id="e58" source="n10" target="n18">
      </edge>
    <edge id="e59" source="n10" target="n19">
      </edge>
    <edge id="e60" source="n10" target="n20">
      </edge>
    <edge id="e61" source="n10" target="n21">
      </edge>
    <edge id="e62" source="n10" target="n22">
      </edge>
    <edge id="e63" source="n10" target="n76">
      </edge>
    <edge id="e64" source="n9" target="n23">
      </edge>
    <edge id="e65" source="n9" target="n24">
      </edge>
    <edge id="e66" source="n23" target="n18">
      </edge>
    <edge id="e67" source="n23" target="n20">
      </edge>
    <edge id="e68" source="n23" target="n17">
      </edge>
    <edge id="e69" source="n23" target="n19">
      </edge>
    <edge id="e70" source="n23" target="n22">
      </edge>
    <edge id="e71" source="n23" target="n76">
      </edge>
    <edge id="n0::e1" source="n0::n5" target="n0::n4">
      </edge>
    <edge id="e72" source="n0::n5" target="n25">
      </edge>
    <edge id="e73" source="n0::n5" target="n26">
      </edge>
    <edge id="e74" source="n0::n5" target="n27">
      </edge>
    <edge id="n0::e2" source="n0::n6" target="n0::n4">
      </edge>
    <edge id="e75" source="n0::n6" target="n28">
      </edge>
    <edge id="e76" source="n3" target="n0::n14">
      </edge>
    <edge id="e77" source="n0::n3" target="n29">
      </edge>
    <edge id="e78" source="n0::n3" target="n30">
      </edge>
    <edge id="e79" source="n0::n3" target="n31">
      </edge>
    <edge id="e80" source="n0::n3" target="n32">
      </edge>
    <edge id="e81" source="n0::n3" target="n33">
      </edge>
    <edge id="e82" source="n0::n3" target="n34">
      </edge>
    <edge id="e83" source="n31" target="n4">
      </edge>
    <edge id="e84" source="n31" target="n5">
      </edge>
    <edge id="e85" source="n30" target="n4">
      </edge>
    <edge id="e86" source="n30" target="n5">
      </edge>
    <edge id="e87" source="n29" target="n4">
      </edge>
    <edge id="e88" source="n29" target="n5">
      </edge>
    <edge id="e89" source="n0::n14" target="n35">
      </edge>
    <edge id="e90" source="n0::n14" target="n36">
      </edge>
    <edge id="e91" source="n0::n14" target="n37">
      </edge>
    <edge id="e92" source="n35" target="n38">
      </edge>
    <edge id="e93" source="n35" target="n39">
      </edge>
    <edge id="e94" source="n40" target="n43">
      </edge>
    <edge id="e95" source="n40" target="n44">
      </edge>
    <edge id="e96" source="n44" target="n4">
      </edge>
    <edge id="e97" source="n44" target="n5">
      </edge>
    <edge id="e98" source="n41" target="n45">
      </edge>
    <edge id="e99" source="n41" target="n44">
      </edge>
    <edge id="e100" source="n41" target="n43">
      </edge>
    <edge id="e101" source="n41" target="n46">
      </edge>
    <edge id="e102" source="n42" target="n47">
      </edge>
    <edge id="e103" source="n42" target="n48">
      </edge>
    <edge id="e104" source="n0::n0" target="n57::n0">
      </edge>
    <edge id="e105" source="n0::n1" target="n57::n1">
      </edge>
    <edge id="e106" source="n49" target="n52">
      </edge>
    <edge id="e107" source="n49" target="n53">
      </edge>
    <edge id="e108" source="n49" target="n54">
      </edge>
    <edge id="e109" source="n49" target="n55">
      </edge>
    <edge id="e110" source="n49" target="n56">
      </edge>
    <edge id="e111" source="n0::n7" target="n50">
      </edge>
    <edge id="e112" source="n0::n7" target="n51">
      </edge>
    <edge id="e113" source="n0::n7" target="n49">
      </edge>
    <edge id="e114" source="n2" target="n57::n2">
      </edge>
    <edge id="e115" source="n32" target="n57::n5">
      </edge>
    <edge id="e116" source="n33" target="n57::n5">
      </edge>
    <edge id="e117" source="n34" target="n57::n4">
      </edge>
    <edge id="e118" source="n16" target="n57::n6">
      </edge>
    <edge id="e119" source="n76" target="n57::n6">
      </edge>
    <edge id="e120" source="n17" target="n57::n7">
      </edge>
    <edge id="e121" source="n19" target="n57::n7">
      </edge>
    <edge id="e122" source="n22" target="n57::n7">
      </edge>
    <edge id="e123" source="n18" target="n57::n7">
      </edge>
    <edge id="e124" source="n20" target="n57::n7">
      </edge>
    <edge id="e125" source="n21" target="n57::n7">
      </edge>
    <edge id="e126" source="n25" target="n57::n10">
      </edge>
    <edge id="e127" source="n26" target="n57::n9">
      </edge>
    <edge id="e128" source="n27" target="n57::n8">
      </edge>
    <edge id="e129" source="n28" target="n57::n11">
      </edge>
    <edge id="e130" source="n52" target="n57::n13">
      </edge>
    <edge id="e131" source="n56" target="n57::n12">
      </edge>
    <edge id="e132" source="n0::n9" target="n57::n16">
      </edge>
    <edge id="e133" source="n0::n10" target="n57::n17">
      </edge>
    <edge id="e134" source="n0::n11" target="n57::n18">
      </edge>
    <edge id="e135" source="n38" target="n57::n21">
      </edge>
    <edge id="e136" source="n39" target="n57::n20">
      </edge>
    <edge id="e137" source="n45" target="n57::n19">
      </edge>
    <edge id="e138" source="n46" target="n57::n20">
      </edge>
    <edge id="e139" source="n47" target="n57::n20">
      </edge>
    <edge id="e140" source="n37" target="n57::n19">
      </edge>
    <edge id="e141" source="n0::n12" target="n57::n22">
      </edge>
    <edge id="e142" source="n7" target="n57::n23">
      </edge>
    <edge id="e143" source="n8" target="n57::n24">
      </edge>
    <edge id="e144" source="n5" target="n57::n5">
      </edge>
    <edge id="e145" source="n4" target="n57::n25">
      </edge>
    <edge id="e146" source="n51" target="n57::n12">
      </edge>
    <edge id="e147" source="n50" target="n57::n13">
      </edge>
    <edge id="e148" source="n49" target="n0::n4">
      </edge>
    <edge id="e149" source="n24" target="n57::n26">
      </edge>
    <edge id="e150" source="n43" target="n57::n27">
      </edge>
    <edge id="e151" source="n49" target="n58">
      </edge>
    <edge id="e152" source="n58" target="n57::n15">
      </edge>
    <edge id="e153" source="n0::n8" target="n59">
      </edge>
    <edge id="e154" source="n59" target="n57::n15">
      </edge>
    <edge id="e155" source="n0::n8" target="n60">
      </edge>
    <edge id="e156" source="n60" target="n57::n14">
      </edge>
    <edge id="e157" source="n0::n8" target="n61">
      </edge>
    <edge id="e158" source="n62" target="n63">
      </edge>
    <edge id="e159" source="n62" target="n64">
      </edge>
    <edge id="e160" source="n49" target="n62">
      </edge>
    <edge id="e161" source="n63" target="n57::n13">
      </edge>
    <edge id="e162" source="n64" target="n57::n12">
      </edge>
    <edge id="e163" source="n0::n7" target="n65">
      </edge>
    <edge id="e164" source="n66" target="n57::n13">
      </edge>
    <edge id="e165" source="n67" target="n32">
      </edge>
    <edge id="e166" source="n67" target="n34">
      </edge>
    <edge id="e167" source="n67" target="n31">
      </edge>
    <edge id="e168" source="n67" target="n29">
      </edge>
    <edge id="e169" source="n67" target="n30">
      </edge>
    <edge id="e170" source="n48" target="n57::n29">
      </edge>
    <edge id="e171" source="n41" target="n42">
      </edge>
    <edge id="e172" source="n40" target="n42">
      </edge>
    <edge id="e173" source="n65" target="n68">
      </edge>
    <edge id="e174" source="n65" target="n69">
      </edge>
    <edge id="e175" source="n68" target="n57::n13">
      </edge>
    <edge id="e176" source="n69" target="n57::n12">
      </edge>
    <edge id="e177" source="n0::n3" target="n70">
      </edge>
    <edge id="e178" source="n70" target="n5">
      </edge>
    <edge id="e179" source="n70" target="n4">
      </edge>
    <edge id="e180" source="n0::n14" target="n71">
      </edge>
    <edge id="e181" source="n71" target="n72">
      </edge>
    <edge id="e182" source="n71" target="n73">
      </edge>
    <edge id="e183" source="n72" target="n36">
      </edge>
    <edge id="e184" source="n72" target="n42">
      </edge>
    <edge id="e185" source="n72" target="n43">
      </edge>
    <edge id="e186" source="n72" target="n44">
      </edge>
    <edge id="e187" source="n72" target="n45">
      </edge>
    <edge id="e188" source="n73" target="n74">
      </edge>
    <edge id="e189" source="n73" target="n75">
      </edge>
    <edge id="e190" source="n74" target="n57::n20">
      </edge>
    <edge id="e191" source="n75" target="n57::n19">
      </edge>
    <edge id="e192" source="n13" target="n77">
      </edge>
    <edge id="e193" source="n11" target="n77">
      </edge>
    <edge id="e194" source="n14" target="n77">
      </edge>
    <edge id="e195" source="n10" target="n77">
      </edge>
    <edge id="e196" source="n15" target="n77">
      </edge>
    <edge id="e197" source="n77" target="n57::n7">
      </edge>
    <edge id="e198" source="n0::n7" target="n78">
      </edge>
    <edge id="e199" source="n78" target="n57::n13">
      </edge>
    <edge id="e200" source="n0::n8" target="n79">
      </edge>
    <edge id="e201" source="n79" target="n57::n15">
      </edge>
    <edge id="e202" source="n80" target="n57::n32">
      </edge>
    <edge id="e203" source="n61" target="n80">
      </edge>
    <edge id="e204" source="n81" target="n57::n15">
      </edge>
    <edge id="e205" source="n61" target="n81">
      </edge>
    <edge id="e206" source="n82" target="n57::n15">
      </edge>
    <edge id="e207" source="n0::n8" target="n82">
      </edge>
    <edge id="e208" source="n53" target="n57::n13">
      </edge>
    <edge id="e209" source="n0::n14" target="n41">
      </edge>
    <edge id="e210" source="n0::n14" target="n40">
      </edge>
    <edge id="e211" source="n0::n14" target="n42">
      </edge>
    <edge id="e212" source="n0::n14" target="n67">
      </edge>
    <edge id="e213" source="n67" target="n33">
      </edge>
    <edge id="e214" source="n67" target="n70">
      </edge>
    <edge id="e215" source="n0::n2" target="n83">
      </edge>
    <edge id="e216" source="n83" target="n57::n13">
      </edge>
    <edge id="e217" source="n1" target="n57::n3">
      </edge>
    <edge id="e218" source="n40" target="n84">
      </edge>
    <edge id="e219" source="n84" target="n57::n19">
      </edge>
    <edge id="e220" source="n36" target="n57::n28">
      </edge>
    <edge id="e221" source="n0::n6" target="n85">
      </edge>
    <edge id="e222" source="n85" target="n57::n33">
      </edge>
    <edge id="e223" source="n0::n8" target="n86">
      </edge>
    <edge id="e224" source="n54" target="n57::n13">
      </edge>
    <edge id="e225" source="n6" target="n87">
      </edge>
    <edge id="e226" source="n6" target="n88">
      </edge>
    <edge id="e227" source="n87" target="n57::n23">
      </edge>
    <edge id="e228" source="n88" target="n57::n24">
      </edge>
    <edge id="e229" source="n55" target="n89">
      </edge>
    <edge id="e230" source="n55" target="n90">
      </edge>
    <edge id="e231" source="n89" target="n57::n13">
      </edge>
    <edge id="e232" source="n90" target="n57::n12">
      </edge>
    <edge id="e233" source="n3" target="n0::n15">
      </edge>
    <edge id="e234" source="n0::n15" target="n91">
      </edge>
    <edge id="e235" source="n0::n15" target="n92">
      </edge>
    <edge id="e236" source="n0::n15" target="n93">
      </edge>
    <edge id="e237" source="n0::n15" target="n94">
      </edge>
    <edge id="e238" source="n0::n15" target="n95">
      </edge>
    <edge id="e239" source="n0::n15" target="n96">
      </edge>
    <edge id="e240" source="n0::n15" target="n97">
      </edge>
    <edge id="e241" source="n0::n15" target="n98">
      </edge>
    <edge id="e242" source="n96" target="n57::n35">
      </edge>
    <edge id="e243" source="n94" target="n57::n35">
      </edge>
    <edge id="e244" source="n98" target="n57::n34">
      </edge>
    <edge id="e245" source="n95" target="n57::n35">
      </edge>
    <edge id="e246" source="n97" target="n57::n35">
      </edge>
    <edge id="e247" source="n92" target="n57::n35">
      </edge>
    <edge id="e248" source="n93" target="n57::n35">
      </edge>
    <edge id="e249" source="n91" target="n57::n35">
      </edge>
    <edge id="e250" source="n86" target="n57::n36">
      </edge>
  </graph>
  <data key="d16">
    <y:Resources/>
  </data>
</graphml>
